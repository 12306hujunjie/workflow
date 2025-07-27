"""异步数据库会话管理"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os


# SQLAlchemy基础模型类
class Base(DeclarativeBase):
    pass


class DatabaseConfig:
    """数据库配置"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "postgresql+asyncpg://postgres:password@localhost:5432/workflow_platform"
        )
        
        # PostgreSQL数据库引擎参数
        engine_kwargs = {
            "echo": os.getenv("DB_ECHO", "false").lower() == "true",
            "future": True,
            "pool_pre_ping": True,
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 3600
        }
        
        self.engine = create_async_engine(self.database_url, **engine_kwargs)
        self.async_session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取异步数据库会话"""
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def session_scope(self):
        """返回一个可以用作上下文管理器的会话"""
        return self.async_session_factory()
    
    async def close(self):
        """关闭数据库连接"""
        await self.engine.dispose()


# 全局数据库配置实例
db_config = DatabaseConfig()