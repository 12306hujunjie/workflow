"""集成测试配置和fixtures"""
import sys

# macOS 下用 pytest-asyncio 或 asyncio 运行异步测试时，事件循环策略与信号处理不兼容，此处修复
if sys.platform == "darwin":
    import asyncio
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import Settings
from shared_kernel.application.exception_handlers import register_exception_handlers
from tests.conftest import test_session as base_test_session, settings as base_settings


def create_test_services(settings: Settings):
    """创建测试服务实例"""
    from bounded_contexts.user_management.infrastructure.repositories.sqlalchemy_user_repository import \
        SQLAlchemyUserRepository
    from bounded_contexts.user_management.infrastructure.auth.password_service import PasswordService
    from bounded_contexts.user_management.infrastructure.auth.jwt_service import JWTService
    from bounded_contexts.user_management.application.services.user_application_service import UserApplicationService
    from shared_kernel.infrastructure.database.async_session import DatabaseConfig

    # 使用测试数据库URL，如果设置了test_database_url则使用它，否则使用默认的database_url
    database_url = settings.test_database_url if settings.test_database_url else settings.database_url

    # 创建数据库配置
    db_config = DatabaseConfig(database_url=database_url)

    # 创建服务实例
    password_service = PasswordService(rounds=settings.bcrypt_rounds)
    jwt_service = JWTService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
        refresh_token_expire_days=settings.jwt_refresh_token_expire_days
    )

    # 创建应用服务工厂 - 模仿正确的依赖注入模式
    async def create_user_service():
        # 使用与dependencies.py相同的会话管理模式
        async for session in db_config.get_session():
            user_repository = SQLAlchemyUserRepository(session)
            yield UserApplicationService(
                user_repository=user_repository,
                password_service=password_service,
                jwt_service=jwt_service
            )

    # 返回服务工厂和数据库配置，以便在应用关闭时清理
    return create_user_service, db_config


# 移除了 clean_test_session fixture，因为：
# 1. 直接删除数据库数据破坏了测试隔离性
# 2. 在有外键约束时可能导致删除失败
# 3. 现有的 test_session 已通过事务回滚提供了完美的测试隔离
# 4. 符合测试最佳实践：依赖事务回滚而非手动清理数据


def create_test_app(settings: Settings):
    """创建测试应用实例"""
    # 创建服务工厂和数据库配置
    create_user_service, db_config = create_test_services(settings)

    @asynccontextmanager
    async def test_lifespan(app: FastAPI):
        # 启动时
        yield

        # 关闭时 - 确保数据库连接池被正确关闭
        await db_config.close()

    # 创建测试应用
    app = FastAPI(
        title="Test App",
        version="1.0.0",
        lifespan=test_lifespan
    )

    # 注册全局异常处理器
    register_exception_handlers(app)

    # 导入路由
    from bounded_contexts.user_management.presentation.api.user_routes import router as user_router
    from bounded_contexts.user_management.presentation.api.auth_routes import router as auth_router
    from bounded_contexts.user_management.presentation.api.admin_routes import router as admin_router

    # 使用 dependency_overrides 绕过容器依赖注入
    from bounded_contexts.user_management.presentation.dependencies import get_user_service

    # 覆盖依赖函数
    # 注意：create_user_service是一个async函数，需要直接作为依赖工厂使用
    app.dependency_overrides[get_user_service] = create_user_service

    # 注册路由
    app.include_router(auth_router, prefix=f"{settings.api_v1_prefix}/auth", tags=["Authentication"])
    app.include_router(user_router, prefix=f"{settings.api_v1_prefix}/users", tags=["User Management"])
    app.include_router(admin_router, prefix=f"{settings.api_v1_prefix}/admin", tags=["Admin"])

    return app


@pytest.fixture(scope="function")
async def api_client(base_settings, base_test_session):
    """API测试客户端 - 使用事务回滚隔离的数据库会话"""
    app = create_test_app(base_settings)

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
