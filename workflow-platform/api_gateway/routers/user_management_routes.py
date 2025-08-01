"""用户管理上下文路由聚合器"""

from fastapi import APIRouter

from bounded_contexts.user_management.presentation.api.auth_routes import router as auth_router
from bounded_contexts.user_management.presentation.api.user_routes import router as user_router
from bounded_contexts.user_management.presentation.api.admin_routes import router as admin_router


def create_user_management_router() -> APIRouter:
    """创建用户管理上下文的路由聚合器"""
    router = APIRouter(prefix="/users", tags=["User Management"])
    
    # 公开认证路由（不需要认证）
    from bounded_contexts.user_management.presentation.api.public_auth_routes import router as public_auth_router
    router.include_router(
        public_auth_router,
        prefix="/public",
        tags=["Public Authentication"]
    )
    
    # 认证相关路由
    from bounded_contexts.user_management.presentation.api.auth_routes import router as auth_router
    router.include_router(
        auth_router,
        prefix="/auth",
        tags=["Authentication"]
    )
    
    # 用户管理路由
    from bounded_contexts.user_management.presentation.api.user_routes import router as user_router
    router.include_router(
        user_router,
        prefix="",
        tags=["Users"]
    )
    
    # 管理员路由
    from bounded_contexts.user_management.presentation.api.admin_routes import router as admin_router
    router.include_router(
        admin_router,
        prefix="/admin",
        tags=["Admin"]
    )
    
    return router