"""Pytest配置和fixtures"""

import asyncio
import pytest
from typing import AsyncGenerator
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from container import Container
from bounded_contexts.user_management.domain.entities.user import User
from shared_kernel.domain.value_objects import (
    Username, Email, HashedPassword
)
from bounded_contexts.user_management.infrastructure.models.user_models import Base
from bounded_contexts.user_management.infrastructure.auth.password_service import PasswordService
from bounded_contexts.user_management.infrastructure.auth.jwt_service import JWTService
from config.settings import Settings


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_container():
    """创建mock容器"""
    container = Container()
    
    # Mock配置
    container.config.override(Settings(
        database_url="sqlite+aiosqlite:///:memory:",
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
    user = User(
        username=Username(value="testuser"),
        email=Email(value="test@example.com"),
        hashed_password=HashedPassword(
            value=password_service.hash_password("Test@123456")
        )
    )
    return user


@pytest.fixture
def mock_user_repository():
    """创建mock用户仓储"""
    repository = AsyncMock()
    repository.find_by_username = AsyncMock(return_value=None)
    repository.find_by_email = AsyncMock(return_value=None)
    repository.find_by_id = AsyncMock(return_value=None)
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