"""异步数据库会话管理"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os


class Base(DeclarativeBase):
    """SQLAlchemy基础模型类"""
    pass


class DatabaseConfig:
    """数据库配置"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "postgresql+asyncpg://postgres:password@localhost:5432/workflow_platform"
        )
        self.engine = create_async_engine(
            self.database_url,
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.async_session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取异步数据库会话"""
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """关闭数据库连接"""
        await self.engine.dispose()


# 全局数据库配置实例
db_config = DatabaseConfig()