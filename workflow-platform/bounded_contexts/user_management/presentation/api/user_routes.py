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
    # 头像上传功能实现
    try:
        # 验证文件类型和大小
        if not avatar.content_type.startswith('image/'):
            raise ValidationException("只支持图片文件")
        
        if avatar.size > 5 * 1024 * 1024:  # 5MB限制
            raise ValidationException("文件大小不能超过5MB")
        
        # 生成文件名
        import uuid
        file_extension = avatar.filename.split('.')[-1] if '.' in avatar.filename else 'jpg'
        filename = f"{current_user_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # 这里可以集成文件存储服务 (如AWS S3, 阿里云OSS等)
        # 生产环境中应该上传到云存储，这里返回本地路径
        avatar_url = f"/static/avatars/{filename}"
        
        # 更新用户头像URL
        from ...application.commands.user_commands import UpdateUserProfileCommand
        command = UpdateUserProfileCommand(avatar_url=avatar_url)
        await user_service.update_user_profile(current_user_id, command)
        
        return ApiResponse.success_response(
            data={"avatar_url": avatar_url},
            message="头像上传成功"
        )
    except Exception as e:
        raise ValidationException(f"头像上传失败: {str(e)}")


@router.delete("/me/avatar", response_model=ApiResponse)
async def delete_avatar(
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """删除头像"""
    # 头像删除功能实现
    try:
        # 删除用户头像
        from ...application.commands.user_commands import UpdateUserProfileCommand
        command = UpdateUserProfileCommand(avatar_url=None)
        await user_service.update_user_profile(current_user_id, command)
        
        return ApiResponse.success_response(
            message="头像删除成功"
        )
    except Exception as e:
        raise ValidationException(f"头像删除失败: {str(e)}")


@router.get("/me/login-history", response_model=ApiResponse)
async def get_login_history(
    page: int = 1,
    limit: int = 20,
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """获取登录历史"""
    # 登录历史功能实现
    try:
        # 这里可以集成真实的登录历史查询
        login_history = await user_service.get_user_login_history(current_user_id, page, limit)
        
        return ApiResponse.success_response(
            data=login_history,
            message="获取登录历史成功"
        )
    except Exception as e:
        raise ValidationException(f"获取登录历史失败: {str(e)}")
