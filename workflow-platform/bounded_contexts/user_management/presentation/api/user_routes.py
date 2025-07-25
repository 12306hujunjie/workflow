"""用户API路由"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from dependency_injector.wiring import inject, Provide

from ..schemas.user_schemas import (
    UserRegisterRequest, UserLoginRequest, UpdateProfileRequest,
    ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest,
    RefreshTokenRequest, UserResponse, UserListResponse, LoginResponse,
    TokenResponse, MessageResponse, UserProfileResponse
)
from ...application.services.user_application_service import UserApplicationService
from ...application.commands.user_commands import (
    RegisterUserCommand, LoginUserCommand, UpdateUserProfileCommand,
    ChangePasswordCommand, ForgotPasswordCommand, ResetPasswordCommand
)
from shared_kernel.domain.value_objects import UserStatus
from container import Container
from api_gateway.middleware.auth_middleware import get_current_user_id


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@inject
async def register_user(
    request: UserRegisterRequest,
    user_service: UserApplicationService = Depends(Provide[Container.user_application_service])
) -> UserResponse:
    """用户注册"""
    try:
        command = RegisterUserCommand(
            username=request.username,
            email=request.email,
            password=request.password
        )
        user = await user_service.register_user(command)
        
        return UserResponse(
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
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.post("/login", response_model=LoginResponse)
@inject
async def login_user(
    request: UserLoginRequest,
    req: Request,
    user_service: UserApplicationService = Depends(Provide[Container.user_application_service])
) -> LoginResponse:
    """用户登录"""
    try:
        command = LoginUserCommand(
            username_or_email=request.username_or_email,
            password=request.password,
            ip_address=req.client.host,
            user_agent=req.headers.get("user-agent")
        )
        result = await user_service.login_user(command)
        
        user = result["user"]
        return LoginResponse(
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
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.post("/refresh", response_model=TokenResponse)
@inject
async def refresh_token(
    request: RefreshTokenRequest,
    user_service: UserApplicationService = Depends(Provide[Container.user_application_service])
) -> TokenResponse:
    """刷新访问令牌"""
    try:
        result = await user_service.refresh_token(request.refresh_token)
        return TokenResponse(
            access_token=result["access_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
@inject
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(Provide[Container.user_application_service])
) -> UserResponse:
    """获取当前用户信息"""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserResponse(
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


@router.put("/me/profile", response_model=UserResponse)
@inject
async def update_profile(
    request: UpdateProfileRequest,
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(Provide[Container.user_application_service])
) -> UserResponse:
    """更新用户资料"""
    try:
        command = UpdateUserProfileCommand(**request.dict(exclude_unset=True))
        user = await user_service.update_user_profile(user_id, command)
        
        return UserResponse(
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
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/me/change-password", response_model=MessageResponse)
@inject
async def change_password(
    request: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(Provide[Container.user_application_service])
) -> MessageResponse:
    """修改密码"""
    try:
        command = ChangePasswordCommand(
            old_password=request.old_password,
            new_password=request.new_password
        )
        await user_service.change_password(user_id, command)
        return MessageResponse(message="密码修改成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/forgot-password", response_model=MessageResponse)
@inject
async def forgot_password(
    request: ForgotPasswordRequest,
    user_service: UserApplicationService = Depends(Provide[Container.user_application_service])
) -> MessageResponse:
    """忘记密码"""
    # TODO: 实现邮件发送逻辑
    return MessageResponse(message="密码重置邮件已发送，请查收")


@router.post("/reset-password", response_model=MessageResponse)
@inject
async def reset_password(
    request: ResetPasswordRequest,
    user_service: UserApplicationService = Depends(Provide[Container.user_application_service])
) -> MessageResponse:
    """重置密码"""
    # TODO: 实现密码重置逻辑
    return MessageResponse(message="密码重置成功")