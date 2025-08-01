"""单元测试专用配置文件

单元测试应该是快速、独立的，不依赖外部资源（如数据库、Redis等）。
这个配置文件提供了单元测试所需的mock对象和fixture。
"""

import pytest
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def mock_database_session():
    """Mock数据库会话，用于单元测试"""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_redis_client():
    """Mock Redis客户端，用于单元测试"""
    redis_client = AsyncMock()
    redis_client.get = AsyncMock(return_value=None)
    redis_client.set = AsyncMock(return_value=True)
    redis_client.delete = AsyncMock(return_value=1)
    redis_client.exists = AsyncMock(return_value=False)
    return redis_client


@pytest.fixture
def mock_email_service():
    """Mock邮件服务，用于单元测试"""
    email_service = AsyncMock()
    email_service.send_verification_email = AsyncMock(return_value=True)
    email_service.send_password_reset_email = AsyncMock(return_value=True)
    return email_service