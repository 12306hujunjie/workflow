"""用户管理API路由"""

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File

from ..schemas.user_schemas import (
    UpdateProfileRequest, ChangePasswordRequest, UserResponse, 
    UserListResponse, MessageResponse, UserProfileResponse
)
from ...application.services.user_application_service import UserApplicationService
from ...application.commands.user_commands import (
    UpdateUserProfileCommand, ChangePasswordCommand
)
from ..dependencies import get_user_service
from shared_kernel.application.api_response import ApiResponse
from shared_kernel.application.exceptions import (
    UserNotFoundException, ValidationException
)
from api_gateway.middleware.auth_middleware import get_current_user_id


router = APIRouter(tags=["user-management"])


# 依赖注入函数已移至 dependencies.py 模块





@router.get("/me", response_model=ApiResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """获取当前用户信息"""
    user_dto = await user_service.get_user_by_id(user_id)
    if not user_dto:
        raise UserNotFoundException(user_id=str(user_id))
    
    # 将 UserProfileDTO 转换为 UserProfileResponse
    profile_response = None
    if user_dto.profile:
        profile_response = UserProfileResponse(
            display_name=user_dto.profile.display_name,
            avatar_url=user_dto.profile.avatar_url,
            bio=user_dto.profile.bio,
            timezone=user_dto.profile.timezone or "UTC",
            language=user_dto.profile.language or "zh-CN",
            notification_preferences=user_dto.profile.notification_preferences or {}
        )
    
    user_data = UserResponse(
        id=user_dto.id,
        username=user_dto.username,
        email=user_dto.email,
        status=user_dto.status,
        role=user_dto.role,
        last_login_at=user_dto.last_login_at,
        created_at=user_dto.created_at,
        updated_at=user_dto.updated_at,
        profile=profile_response
    )
    
    return ApiResponse.success_response(
        data=user_data.model_dump(),
        message="获取用户信息成功"
    )


@router.put("/me/profile", response_model=ApiResponse)
async def update_profile(
    request: UpdateProfileRequest,
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """更新用户资料"""
    command = UpdateUserProfileCommand(**request.model_dump(exclude_unset=True))
    user_dto = await user_service.update_user_profile(user_id, command)
    
    # 将 UserProfileDTO 转换为 UserProfileResponse
    profile_response = None
    if user_dto.profile:
        profile_response = UserProfileResponse(
            display_name=user_dto.profile.display_name,
            avatar_url=user_dto.profile.avatar_url,
            bio=user_dto.profile.bio,
            timezone=user_dto.profile.timezone or "UTC",
            language=user_dto.profile.language or "zh-CN",
            notification_preferences=user_dto.profile.notification_preferences or {}
        )
    
    user_data = UserResponse(
        id=user_dto.id,
        username=user_dto.username,
        email=user_dto.email,
        status=user_dto.status,
        role=user_dto.role,
        last_login_at=user_dto.last_login_at,
        created_at=user_dto.created_at,
        updated_at=user_dto.updated_at,
        profile=profile_response
    )
    
    return ApiResponse.success_response(
        data=user_data.model_dump(),
        message="用户资料更新成功"
    )


@router.post("/me/change-password", response_model=ApiResponse)
async def change_password(
    request: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """修改密码"""
    command = ChangePasswordCommand(
        old_password=request.old_password,
        new_password=request.new_password
    )
    await user_service.change_password(user_id, command)
    
    return ApiResponse.success_response(
        message="密码修改成功"
    )


@router.delete("/me/account", response_model=ApiResponse)
async def delete_account(
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """删除账户"""
    await user_service.delete_user_account(current_user_id)
    
    return ApiResponse.success_response(
        message="账户删除成功"
    )


@router.get("/me/activity", response_model=ApiResponse)
async def get_user_activity(
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """获取用户活动"""
    activity = await user_service.get_user_activity(current_user_id)
    
    return ApiResponse.success_response(
        data=activity,
        message="获取用户活动成功"
    )


@router.post("/me/avatar", response_model=ApiResponse)
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """上传头像"""
    # TODO: 实现头像上传功能
    # 这里暂时返回一个模拟的响应
    return ApiResponse.success_response(
        data={"avatar_url": f"/static/avatars/{current_user_id}.jpg"},
        message="头像上传成功"
    )


@router.delete("/me/avatar", response_model=ApiResponse)
async def delete_avatar(
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """删除头像"""
    # TODO: 实现头像删除功能
    return ApiResponse.success_response(
        message="头像删除成功"
    )


@router.get("/me/login-history", response_model=ApiResponse)
async def get_login_history(
    page: int = 1,
    limit: int = 20,
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """获取登录历史"""
    # TODO: 实现登录历史功能
    # 这里暂时返回一个模拟的响应
    return ApiResponse.success_response(
        data={
            "items": [],
            "total": 0,
            "page": page,
            "limit": limit
        },
        message="获取登录历史成功"
    )
