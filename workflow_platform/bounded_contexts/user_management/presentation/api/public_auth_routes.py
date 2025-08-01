"""公开认证API路由 - 不需要认证的端点"""

from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import ValidationError

from shared_kernel.application.api_response import ApiResponse
from ..dependencies import get_user_service
from ..schemas.user_schemas import (
    ResendVerificationCodeRequest, LogoutRequest
)
from ...application.services.user_application_service import UserApplicationService

router = APIRouter(tags=["public-authentication"])


@router.post("/logout", response_model=ApiResponse)
async def public_logout(
        request: Request,
        logout_request: LogoutRequest = None,
        user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """公开登出端点 - 不需要认证"""
    # 处理可选的logout_request参数
    if logout_request is None:
        logout_request = LogoutRequest()
    
    # 获取当前access token（如果存在）
    authorization = request.headers.get("Authorization")
    access_token = None
    user_id = None
    
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization[7:]
        
        # 尝试从token中获取用户ID（不验证有效性）
        try:
            # 使用依赖注入容器获取JWT服务
            jwt_service = user_service._jwt_service
            
            # 直接解码token（不验证有效性）
            payload = jwt_service.decode_token(access_token)
            user_id = payload.get("user_id")
        except Exception:
            # Token无效或过期，但仍继续处理logout
            pass
    
    # 执行logout操作（即使token无效也要尝试清理）
    if access_token:
        try:
            if user_id:
                # 如果有用户ID，使用完整的logout流程
                await user_service.logout_user(user_id, access_token, logout_request.refresh_token)
            else:
                # 如果没有用户ID，至少尝试将token加入黑名单
                jwt_service = user_service._jwt_service
                await jwt_service.blacklist_token(access_token)
        except Exception as e:
            # 即使logout服务失败，也返回成功（前端会清理本地token）
            print(f"Logout service error (ignored): {e}")
            pass

    return ApiResponse.success_response(
        message="登出成功"
    )


@router.post("/send-verification-code", response_model=ApiResponse)
async def public_send_verification_code(
        request: ResendVerificationCodeRequest,
        http_request: Request,
        user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """发送验证码（带严格邮箱验证）"""
    client_ip = http_request.client.host
    
    # 严格的邮箱验证 - 确保通过 Pydantic EmailStr 验证
    try:
        # 这里request.email已经通过了Pydantic EmailStr验证
        # 但我们再次验证以确保安全
        from pydantic import EmailStr, ValidationError as PydanticValidationError
        
        # 直接验证邮箱
        test_email = EmailStr._validate(request.email, None)
        if not test_email:
            raise ValueError("Invalid email format")
            
    except (PydanticValidationError, ValueError, TypeError) as e:
        # 如果邮箱验证失败，返回422错误
        raise HTTPException(
            status_code=422, 
            detail={
                "message": "请输入有效的邮箱地址",
                "field": "email",
                "value": request.email
            }
        )
    
    # 检查IP频率限制（3分钟）
    try:
        message = await user_service.send_verification_code_with_rate_limit(
            email=request.email, 
            purpose=request.purpose, 
            client_ip=client_ip
        )
        
        return ApiResponse.success_response(message=message)
    except ValueError as e:
        # 频率限制或其他业务错误
        raise HTTPException(status_code=429, detail=str(e))