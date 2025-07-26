"""Pytest配置和fixtures"""

import pytest
from typing import AsyncGenerator
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from container import Container
from bounded_contexts.user_management.domain.entities.user import User
from bounded_contexts.user_management.infrastructure.models.user_models import (
    Base, UserModel, UserProfileModel, UserSessionModel, 
    UserLoginHistoryModel, PasswordResetTokenModel, EmailVerificationTokenModel
)
from bounded_contexts.user_management.infrastructure.auth.password_service import PasswordService
from bounded_contexts.user_management.infrastructure.auth.jwt_service import JWTService
from config.settings import Settings


@pytest.fixture(scope="function")
async def test_engine():
    """测试数据库引擎 - 使用PostgreSQL"""
    import os
    
    database_url = os.getenv(
        "TEST_DATABASE_URL", 
        "postgresql+asyncpg://postgres:password@localhost:5432/workflow_platform_test"
    )
    
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_size=1,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    # 创建所有表（只在session开始时创建一次）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 清理 - 确保在事件循环关闭前完成
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except Exception:
        pass  # 忽略清理时的错误
    finally:
        await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话 - 使用连接级别的事务"""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    
    async_session = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    session = async_session()
    
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()


@pytest.fixture
def mock_container():
    """创建mock容器"""
    container = Container()
    
    # Mock配置
    container.config.override(Settings(
        database_url="postgresql+asyncpg://postgres:password@localhost:5432/workflow_platform_test",
        jwt_secret_key="test-secret-key",
        jwt_algorithm="HS256",
        jwt_expire_minutes=30,
        jwt_refresh_expire_days=7,
        cors_allowed_origins=["http://localhost:3000"],
        redis_url="redis://localhost:6379/0"
    ))
    
    yield container
    
    container.unwire()


@pytest.fixture
def password_service():
    """创建密码服务实例"""
    return PasswordService()


@pytest.fixture
def jwt_service():
    """创建JWT服务实例"""
    return JWTService(secret_key="test-secret-key", algorithm="HS256")


@pytest.fixture
async def test_user(password_service):
    """创建测试用户"""
    user = User.create(
        username="testuser",
        email="test@example.com",
        hashed_password=password_service.hash_password("Test@123456")
    )
    return user


@pytest.fixture
def mock_user_repository():
    """创建mock用户仓储"""
    repository = AsyncMock()
    # 统一使用get_by_*方法名
    repository.get_by_username = AsyncMock(return_value=None)
    repository.get_by_email = AsyncMock(return_value=None)
    repository.get_by_id = AsyncMock(return_value=None)
    repository.exists_by_username = AsyncMock(return_value=False)
    repository.exists_by_email = AsyncMock(return_value=False)
    repository.save = AsyncMock()
    repository.delete = AsyncMock()
    return repository


@pytest.fixture
def mock_unit_of_work(mock_user_repository):
    """创建mock工作单元"""
    uow = AsyncMock()
    uow.users = mock_user_repository
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow