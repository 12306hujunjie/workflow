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
from shared_kernel.infrastructure.redis_service import RedisService
from event_driven_coordination.coordinator import EventDrivenCoordinator, get_coordinator


class Container(containers.DeclarativeContainer):
    """应用依赖注入容器"""
    
    # 配置
    config = providers.Singleton(Settings)
    
    # 数据库
    database_config = providers.Singleton(
        DatabaseConfig,
        database_url=config.provided.database_url
    )
    
    # Redis服务
    redis_service = providers.Singleton(
        RedisService,
        redis_url=config.provided.redis_url
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
        refresh_token_expire_days=config.provided.jwt_refresh_token_expire_days,
        redis_service=redis_service
    )
    
    # 用户仓储
    user_repository = providers.Factory(
        SQLAlchemyUserRepository,
        session_factory=database_config.provided.get_session
    )
    
    # 用户应用服务
    user_application_service = providers.Factory(
        UserApplicationService,
        user_repository=user_repository,
        password_service=password_service,
        jwt_service=jwt_service
    )
    
    # 事件驱动协调器
    event_coordinator = providers.Singleton(
        lambda: get_coordinator()
    )


# 全局容器实例
container = Container()


def init_container() -> Container:
    """初始化容器"""
    # 直接使用settings实例，不需要from_dict
    return container