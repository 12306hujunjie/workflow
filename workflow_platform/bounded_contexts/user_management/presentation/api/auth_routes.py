"""认证API路由"""

from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import validate_email

from api_gateway.middleware.auth_middleware import get_current_user_id
from shared_kernel.application.api_response import ApiResponse
from ..dependencies import get_user_service
from ..schemas.user_schemas import (
    RegisterUserRequest, UserLoginRequest, ForgotPasswordRequest,
    ResetPasswordRequest, RefreshTokenRequest, EmailVerificationRequest,
    EmailVerificationCodeRequest, ResetPasswordWithCodeRequest, ResendVerificationCodeRequest,
    LogoutRequest, LoginResponse, TokenResponse, UserResponse, UserProfileResponse
)
from ...application.commands.user_commands import (
    RegisterUserCommand, LoginUserCommand
)
from ...application.services.user_application_service import UserApplicationService

router = APIRouter(tags=["authentication"])


# 依赖注入函数已移至 dependencies.py 模块


@router.post("/register", response_model=ApiResponse)
async def register(
        request: RegisterUserRequest,
        user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """用户注册（包含验证码验证）"""
    # 先验证验证码（注册场景不检查用户存在性）
    await user_service.verify_code_only(request.email, request.code, "register")
    
    # 验证码正确后进行注册
    command = RegisterUserCommand(
        username=request.username,
        email=request.email,
        password=request.password
    )
    user = await user_service.register_user(command)

    user_data = UserResponse(
        id=user.id,
        username=user.username.value,
        email=user.email.value,
        status=user.status.value,
        role=user.role.value,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        profile=UserProfileResponse.model_validate(user.profile) if user.profile else None
    )

    return ApiResponse.success_response(
        data=user_data.model_dump(),
        message="注册成功"
    )


@router.post("/login", response_model=ApiResponse)
async def login_user(
        request: UserLoginRequest,
        req: Request,
        user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """用户登录"""
    command = LoginUserCommand(
        username_or_email=request.username_or_email,
        password=request.password,
        ip_address=req.client.host,
        user_agent=req.headers.get("user-agent")
    )
    result = await user_service.login_user(command)

    user = result["user"]
    login_data = LoginResponse(
        user=UserResponse(
            id=user.id,
            username=user.username.value,
            email=user.email.value,
            status=user.status.value,
            role=user.role.value,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            profile=UserProfileResponse.model_validate(user.profile) if user.profile else None
        ),
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type=result["token_type"],
        expires_in=result["expires_in"]
    )

    return ApiResponse.success_response(
        data=login_data.model_dump(),
        message="登录成功"
    )


@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(
        request: RefreshTokenRequest,
        user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """刷新访问令牌"""
    result = await user_service.refresh_token(request.refresh_token)

    token_data = TokenResponse(
        access_token=result["access_token"],
        token_type=result["token_type"],
        expires_in=result["expires_in"]
    )

    return ApiResponse.success_response(
        data=token_data.model_dump(),
        message="令牌刷新成功"
    )


@router.post("/logout", response_model=ApiResponse)
async def logout(
        request: Request,
        logout_request: LogoutRequest = None,
        user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """用户登出 - 不需要有效认证"""
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




@router.post("/reset-password", response_model=ApiResponse)
async def reset_password(
        request: ResetPasswordWithCodeRequest,
        user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """重置密码（包含验证码验证）"""
    await user_service.reset_password_with_code(request.email, request.code, request.new_password)

    return ApiResponse.success_response(
        message="密码重置成功"
    )




@router.post("/send-verification-code", response_model=ApiResponse)
async def send_verification_code(
        request: ResendVerificationCodeRequest,
        http_request: Request,
        user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """发送验证码（带IP频率限制）"""
    client_ip = http_request.client.host
    
    # 检查IP频率限制（3分钟）
    try:
        message = await user_service.send_verification_code_with_rate_limit(
            email=str(request.email),
            purpose=request.purpose,
            client_ip=client_ip
        )
        
        return ApiResponse.success_response(message=message)
    except ValueError as e:
        # 频率限制或其他业务错误
        raise HTTPException(status_code=429, detail=str(e))


@router.get("/check-username", response_model=ApiResponse)
async def check_username_availability(
        username: str,
        user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """检查用户名是否可用"""
    is_available = await user_service.check_username_availability(username)
    
    return ApiResponse.success_response(
        data={"available": is_available},
        message="用户名检查完成"
    )


@router.get("/check-email", response_model=ApiResponse)
async def check_email_availability(
        email: str,
        user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """检查邮箱是否可用"""
    is_available = await user_service.check_email_availability(email)
    
    return ApiResponse.success_response(
        data={"available": is_available},
        message="邮箱检查完成"
    )


# PUBLIC ENDPOINTS - NO AUTHENTICATION REQUIRED

@router.post("/public-logout", response_model=ApiResponse)
async def public_logout(
        request: Request,
        user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """公开登出端点 - 不需要认证"""
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
                await user_service.logout_user(user_id, access_token, None)
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


@router.post("/public-send-verification-code", response_model=ApiResponse)
async def public_send_verification_code(
        http_request: Request,
        user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """发送验证码（公开端点，严格验证）"""
    client_ip = http_request.client.host
    
    # 手动解析请求体以进行严格验证
    try:
        body = await http_request.json()
        email = body.get("email", "")
        purpose = body.get("purpose", "")
        
        # 严格的邮箱验证
        from pydantic import EmailStr, ValidationError as PydanticValidationError
        
        # 验证邮箱格式
        try:
            validated_email = EmailStr._validate(email, None)
        except (PydanticValidationError, ValueError, TypeError) as e:
            raise HTTPException(
                status_code=422, 
                detail="请输入有效的邮箱地址"
            )
        
        # 验证purpose
        if purpose not in ["register", "reset_password"]:
            raise HTTPException(
                status_code=422, 
                detail="无效的验证码用途"
            )
        
        # 检查IP频率限制（3分钟）
        message = await user_service.send_verification_code_with_rate_limit(
            email=validated_email, 
            purpose=purpose, 
            client_ip=client_ip
        )
        
        return ApiResponse.success_response(message=message)
        
    except HTTPException:
        raise
    except ValueError as e:
        # 频率限制或其他业务错误
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        # 其他错误
        raise HTTPException(status_code=400, detail="请求格式错误")
