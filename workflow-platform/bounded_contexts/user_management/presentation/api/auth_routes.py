"""认证API路由"""

from typing import Optional
from fastapi import APIRouter, Depends, Request, status

from ..schemas.user_schemas import (
    RegisterUserRequest, UserLoginRequest, ForgotPasswordRequest, 
    ResetPasswordRequest, RefreshTokenRequest, EmailVerificationRequest,
    LogoutRequest, LoginResponse, TokenResponse, MessageResponse, UserResponse, UserProfileResponse
)
from ...application.services.user_application_service import UserApplicationService
from ...application.commands.user_commands import (
    RegisterUserCommand, LoginUserCommand, ForgotPasswordCommand, 
    ResetPasswordCommand
)
from ..dependencies import get_user_service
from shared_kernel.application.api_response import ApiResponse
from shared_kernel.application.exceptions import (
    UserAlreadyExistsException, InvalidCredentialsException,
    UserNotFoundException, ValidationException
)
from api_gateway.middleware.auth_middleware import get_current_user_id


router = APIRouter(tags=["authentication"])


# 依赖注入函数已移至 dependencies.py 模块


@router.post("/register", response_model=ApiResponse)
async def register(
    request: RegisterUserRequest,
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """用户注册"""
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
        profile=UserProfileResponse.from_orm(user.profile) if user.profile else None
    )
    
    return ApiResponse.success_response(
        data=user_data.model_dump(),
        message="注册成功"  # TODO: 暂时跳过邮箱验证提示
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
            profile=UserProfileResponse.from_orm(user.profile) if user.profile else None
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
    logout_request: LogoutRequest,
    request: Request,
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """用户登出"""
    # 获取当前access token
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization[7:]
        await user_service.logout_user(user_id, access_token, logout_request.refresh_token)
    
    return ApiResponse.success_response(
        message="登出成功"
    )


@router.post("/forgot-password", response_model=ApiResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """忘记密码"""
    message = await user_service.forgot_password(request.email)
    
    return ApiResponse.success_response(
        message=message
    )


@router.post("/reset-password", response_model=ApiResponse)
async def reset_password(
    request: ResetPasswordRequest,
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """重置密码"""
    await user_service.reset_password(request.token, request.new_password)
    
    return ApiResponse.success_response(
        message="密码重置成功"
    )


@router.post("/verify-email", response_model=ApiResponse)
async def verify_email(
    request: EmailVerificationRequest,
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """验证邮箱"""
    # TODO: 邮箱验证功能暂时跳过，待后续实现
    await user_service.verify_email(request.token)
    
    return ApiResponse.success_response(
        message="邮箱验证成功"
    )


@router.post("/resend-verification", response_model=ApiResponse)
async def resend_verification(
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """重新发送验证邮件"""
    # TODO: 邮箱验证功能暂时跳过，待后续实现
    await user_service.resend_verification_email(user_id)
    
    return ApiResponse.success_response(
        message="验证邮件已重新发送"
    )