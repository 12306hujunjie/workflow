"""管理员API路由"""

from typing import Optional
from fastapi import APIRouter, Depends, Query

from ..schemas.user_schemas import (
    UserResponse, UserListResponse, UserProfileResponse
)
from ...application.services.user_application_service import UserApplicationService
from ..dependencies import get_user_service
from shared_kernel.application.api_response import ApiResponse, PaginatedResponse
from shared_kernel.application.exceptions import (
    UserNotFoundException, AuthorizationException
)
from shared_kernel.domain.value_objects import UserStatus, UserRole
from api_gateway.middleware.auth_middleware import get_current_user_id


router = APIRouter(prefix="/users", tags=["admin-user-management"])


# 依赖注入函数已移至 dependencies.py 模块


async def require_admin_role(
    user_id: int = Depends(get_current_user_id),
    user_service: UserApplicationService = Depends(get_user_service)
):
    """验证管理员权限"""
    user = await user_service.get_user_by_id(user_id)
    if not user or user.role.value != UserRole.ADMIN.value:
        raise AuthorizationException("需要管理员权限")
    return user_id


@router.get("/list", response_model=ApiResponse)
async def get_users_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="用户状态过滤"),
    role: Optional[str] = Query(None, description="用户角色过滤"),
    search: Optional[str] = Query(None, description="搜索关键词（用户名或邮箱）"),
    admin_user_id: int = Depends(require_admin_role),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """获取用户列表（管理员）"""
    # TODO: 实现用户列表查询逻辑
    # users, total = await user_service.get_users_list(
    #     page=page,
    #     page_size=page_size,
    #     status=status,
    #     role=role,
    #     search=search
    # )
    
    # 临时返回空列表
    users = []
    total = 0
    
    user_list = []
    for user in users:
        user_list.append(UserResponse(
            id=user.id,
            username=user.username.value,
            email=user.email.value,
            status=user.status.value,
            role=user.role.value,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            profile=UserProfileResponse.from_orm(user.profile) if user.profile else None
        ).model_dump())
    
    paginated_data = PaginatedResponse.create(
        items=user_list,
        total=total,
        page=page,
        page_size=page_size
    )
    
    return ApiResponse.success_response(
        data=paginated_data.model_dump(),
        message="获取用户列表成功"
    )


@router.get("/{user_id}", response_model=ApiResponse)
async def get_user_detail(
    user_id: int,
    admin_user_id: int = Depends(require_admin_role),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """获取用户详情（管理员）"""
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
        message="获取用户详情成功"
    )


@router.post("/{user_id}/activate", response_model=ApiResponse)
async def activate_user(
    user_id: int,
    admin_user_id: int = Depends(require_admin_role),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """激活用户（管理员）"""
    await user_service.activate_user(user_id)
    
    return ApiResponse.success_response(
        message="用户激活成功"
    )


@router.post("/{user_id}/deactivate", response_model=ApiResponse)
async def deactivate_user(
    user_id: int,
    admin_user_id: int = Depends(require_admin_role),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """禁用用户（管理员）"""
    await user_service.deactivate_user(user_id)
    
    return ApiResponse.success_response(
        message="用户禁用成功"
    )


@router.post("/{user_id}/ban", response_model=ApiResponse)
async def ban_user(
    user_id: int,
    admin_user_id: int = Depends(require_admin_role),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """封禁用户（管理员）"""
    await user_service.ban_user(user_id)
    
    return ApiResponse.success_response(
        message="用户封禁成功"
    )


@router.get("/stats/overview", response_model=ApiResponse)
async def get_user_stats(
    admin_user_id: int = Depends(require_admin_role),
    user_service: UserApplicationService = Depends(get_user_service)
) -> ApiResponse:
    """获取用户统计信息（管理员）"""
    # TODO: 实现用户统计逻辑
    stats = {
        "total_users": 0,
        "active_users": 0,
        "inactive_users": 0,
        "banned_users": 0,
        "new_users_today": 0,
        "new_users_this_week": 0,
        "new_users_this_month": 0
    }
    
    # active_count = await user_service.count_users_by_status(UserStatus.ACTIVE)
    # inactive_count = await user_service.count_users_by_status(UserStatus.INACTIVE)
    # banned_count = await user_service.count_users_by_status(UserStatus.BANNED)
    
    return ApiResponse.success_response(
        data=stats,
        message="获取用户统计成功"
    )