"""集成测试专用配置文件

集成测试需要真实的外部依赖（如数据库、Redis等）来验证组件间的交互。
这个配置文件提供了集成测试所需的真实服务连接和配置。
"""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


@pytest.fixture(scope="session")
async def init_test_database(settings):
    """集成测试会话前初始化数据库（建库建表）"""
    from bounded_contexts.user_management.infrastructure.models.user_models import Base

    engine = create_async_engine(settings.test_database_url or settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_engine(settings, init_test_database):
    """集成测试专用数据库引擎"""
    engine = create_async_engine(
        settings.test_database_url or settings.database_url,
        echo=False,  # 集成测试时不输出SQL日志
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=300
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine):
    """集成测试专用数据库会话 - 使用连接级别的事务"""
    from sqlalchemy.ext.asyncio import async_sessionmaker

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


@pytest.fixture
def integration_base_settings(settings):
    """集成测试基础设置"""
    return settings


@pytest.fixture
def integration_base_test_session(test_session):
    """集成测试基础会话别名"""
    return test_session


@pytest.fixture
def base_settings(settings):
    """基础设置fixture别名，用于集成测试API测试"""
    return settings
