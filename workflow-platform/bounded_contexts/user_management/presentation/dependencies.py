"""用户管理模块的FastAPI依赖注入"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..application.services.user_application_service import UserApplicationService
from ..infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from shared_kernel.infrastructure.database.async_session import db_config
from shared_kernel.infrastructure.email_service import MockEmailService, SMTPEmailService
from config.email_settings import email_settings
from container import container


async def get_db_session() -> AsyncSession:
    """获取数据库会话的依赖函数
    
    使用FastAPI的依赖注入机制管理数据库会话生命周期，
    确保会话在请求结束时正确关闭，避免连接泄漏。
    """
    async for session in db_config.get_session():
        yield session


async def get_user_service(
    session: AsyncSession = Depends(get_db_session)
) -> UserApplicationService:
    """获取用户应用服务的依赖函数
    
    使用FastAPI管理的数据库会话创建用户应用服务，
    从容器获取其他服务实例（密码服务、JWT服务）。
    """
    # 使用FastAPI管理的数据库会话创建仓储
    user_repository = SQLAlchemyUserRepository(session)
    
    # 从容器获取其他服务实例
    password_service = container.password_service()
    jwt_service = container.jwt_service()
    
    # 根据配置选择邮件服务实现
    if email_settings.USE_MOCK_EMAIL:
        email_service = MockEmailService()
    else:
        email_config = email_settings.to_email_config()
        email_service = SMTPEmailService(email_config)
    
    return UserApplicationService(
        user_repository=user_repository,
        password_service=password_service,
        jwt_service=jwt_service,
        email_service=email_service
    )