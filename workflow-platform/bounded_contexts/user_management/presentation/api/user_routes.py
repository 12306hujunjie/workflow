"""用户管理API路由"""

from typing import Optional
from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from ..schemas.user_schemas import (
    UpdateProfileRequest, ChangePasswordRequest, UserResponse, 
    UserListResponse, MessageResponse, UserProfileResponse
)
from ...application.services.user_application_service import UserApplicationService
from ...application.commands.user_commands import (
    UpdateUserProfileCommand, ChangePasswordCommand
)
from shared_kernel.application.api_response import ApiResponse
from shared_kernel.application.exceptions import (
    UserNotFoundException, ValidationException
)
from container import container
from api_gateway.middleware.auth_middleware import get_current_user_id


router = APIRouter(tags=["user-management"])





@router.get("/me", response_model=ApiResponse)
@inject
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(Provide[container.user_application_service])
) -> ApiResponse:
    """获取当前用户信息"""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise UserNotFoundException(user_id=str(user_id))
    
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
        message="获取用户信息成功"
    )


@router.put("/me/profile", response_model=ApiResponse)
@inject
async def update_profile(
    request: UpdateProfileRequest,
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(Provide[container.user_application_service])
) -> ApiResponse:
    """更新用户资料"""
    command = UpdateUserProfileCommand(**request.model_dump(exclude_unset=True))
    user = await user_service.update_user_profile(user_id, command)
    
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
        message="用户资料更新成功"
    )


@router.post("/me/change-password", response_model=ApiResponse)
@inject
async def change_password(
    request: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(Provide[container.user_application_service])
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