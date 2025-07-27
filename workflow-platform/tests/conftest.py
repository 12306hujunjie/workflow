"""Pytest配置和fixtures"""

from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# 在测试开始前加载环境变量
load_dotenv()

from container import Container
from bounded_contexts.user_management.domain.entities.user import User
from bounded_contexts.user_management.infrastructure.models.user_models import (
    Base
)
from bounded_contexts.user_management.infrastructure.auth.password_service import PasswordService
from bounded_contexts.user_management.infrastructure.auth.jwt_service import JWTService
from config.settings import Settings


@pytest.fixture(scope="session")
async def init_test_database(settings):
    """测试会话前初始化数据库（建库建表）"""
    engine = create_async_engine(settings.test_database_url or settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_engine(settings, init_test_database):
    """全局测试数据库引擎"""
    engine = create_async_engine(
        settings.test_database_url or settings.database_url,
        echo=False,
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=300
    )
    yield engine
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
    try:
        async with async_session() as session:
            yield session
        await transaction.rollback()
    finally:
        await connection.close()


@pytest.fixture(scope="session")
def settings():
    """全局Settings配置fixture"""
    return Settings()


@pytest.fixture
def mock_container(settings):
    """创建mock容器"""
    container = Container()

    # Mock配置，使用公共的settings fixture
    container.config.override(settings)

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
