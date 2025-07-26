"""单元测试专用fixtures - 不依赖数据库"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock
from typing import AsyncGenerator

from bounded_contexts.user_management.domain.entities.user import User
from shared_kernel.domain.value_objects import (
    Username, Email, HashedPassword, UserStatus, UserRole
)
from bounded_contexts.user_management.infrastructure.auth.password_service import PasswordService
from bounded_contexts.user_management.infrastructure.auth.jwt_service import JWTService


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_user_repository():
    """创建mock用户仓储"""
    repository = AsyncMock()
    
    # 设置默认的mock行为
    repository.save = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.get_by_username = AsyncMock()
    repository.get_by_email = AsyncMock()
    repository.exists_by_username = AsyncMock(return_value=False)
    repository.exists_by_email = AsyncMock(return_value=False)
    repository.delete = AsyncMock()
    repository.find_all = AsyncMock(return_value=[])
    repository.find_by_status = AsyncMock(return_value=[])
    repository.count_by_status = AsyncMock(return_value=0)
    
    return repository


@pytest.fixture
def password_service():
    """创建密码服务实例"""
    return PasswordService()


@pytest.fixture
def jwt_service():
    """创建JWT服务实例"""
    return JWTService(
        secret_key="test-secret-key",
        algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7
    )


@pytest.fixture
def test_user(password_service):
    """创建测试用户"""
    # 使用真实的密码哈希以便测试密码验证
    hashed_password = password_service.hash_password("Test@123456")
    return User.create(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        role=UserRole.USER
    )


@pytest.fixture
def mock_redis_service():
    """创建mock Redis服务"""
    redis_service = AsyncMock()
    redis_service.set = AsyncMock()
    redis_service.get = AsyncMock()
    redis_service.delete = AsyncMock()
    redis_service.exists = AsyncMock()
    redis_service.expire = AsyncMock()
    return redis_service