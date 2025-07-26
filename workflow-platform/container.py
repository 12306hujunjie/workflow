"""依赖注入容器配置"""

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import Settings, get_settings
from shared_kernel.infrastructure.database.async_session import DatabaseConfig

# User Management
from bounded_contexts.user_management.domain.repositories.user_repository import UserRepository
from bounded_contexts.user_management.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from bounded_contexts.user_management.infrastructure.auth.password_service import PasswordService
from bounded_contexts.user_management.infrastructure.auth.jwt_service import JWTService
from bounded_contexts.user_management.application.services.user_application_service import UserApplicationService


class Container(containers.DeclarativeContainer):
    """应用依赖注入容器"""
    
    # 配置
    config = providers.Singleton(Settings)
    
    # 数据库
    database_config = providers.Singleton(
        DatabaseConfig,
        database_url=config.provided.database_url
    )
    
    # 数据库会话
    async_session = providers.Factory(
        lambda db_config=database_config: db_config().async_session_factory()
    )
    
    # 认证服务
    password_service = providers.Singleton(
        PasswordService,
        rounds=config.provided.bcrypt_rounds
    )
    
    jwt_service = providers.Singleton(
        JWTService,
        secret_key=config.provided.jwt_secret_key,
        algorithm=config.provided.jwt_algorithm,
        access_token_expire_minutes=config.provided.jwt_access_token_expire_minutes,
        refresh_token_expire_days=config.provided.jwt_refresh_token_expire_days
    )
    
    # 用户管理
    user_repository = providers.Factory(
        SQLAlchemyUserRepository,
        session=async_session
    )
    
    user_application_service = providers.Factory(
        UserApplicationService,
        user_repository=user_repository,
        password_service=password_service,
        jwt_service=jwt_service
    )


# 全局容器实例
container = Container()


def init_container() -> Container:
    """初始化容器"""
    # 直接使用settings实例，不需要from_dict
    return container