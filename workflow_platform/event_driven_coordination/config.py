"""事件驱动架构配置

管理事件驱动架构的各种配置选项
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class EventStoreType(Enum):
    """事件存储类型"""
    SQL = "sql"
    MEMORY = "memory"


class EventPublisherType(Enum):
    """事件发布器类型"""
    REDIS = "redis"
    MEMORY = "memory"


@dataclass
class DatabaseConfig:
    """数据库配置"""
    url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:password@localhost:5432/workflow_platform"
    )
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"


@dataclass
class RedisConfig:
    """Redis 配置"""
    url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    db: int = int(os.getenv("REDIS_DB", "0"))
    password: Optional[str] = os.getenv("REDIS_PASSWORD")
    socket_timeout: float = float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0"))
    socket_connect_timeout: float = float(os.getenv("REDIS_CONNECT_TIMEOUT", "5.0"))
    retry_on_timeout: bool = os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true"
    health_check_interval: int = int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "30"))
    max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
    
    # Pub/Sub 配置
    channel_prefix: str = os.getenv("REDIS_CHANNEL_PREFIX", "events")
    batch_size: int = int(os.getenv("REDIS_BATCH_SIZE", "100"))
    publish_timeout: float = float(os.getenv("REDIS_PUBLISH_TIMEOUT", "5.0"))


@dataclass
class EventProcessingConfig:
    """事件处理配置"""
    # 处理器配置
    max_retry_attempts: int = int(os.getenv("EVENT_MAX_RETRY_ATTEMPTS", "3"))
    retry_delay_seconds: float = float(os.getenv("EVENT_RETRY_DELAY_SECONDS", "1.0"))
    retry_backoff_multiplier: float = float(os.getenv("EVENT_RETRY_BACKOFF_MULTIPLIER", "2.0"))
    max_retry_delay_seconds: float = float(os.getenv("EVENT_MAX_RETRY_DELAY_SECONDS", "60.0"))
    
    # 批处理配置
    batch_size: int = int(os.getenv("EVENT_BATCH_SIZE", "50"))
    batch_timeout_seconds: float = float(os.getenv("EVENT_BATCH_TIMEOUT_SECONDS", "5.0"))
    
    # 并发配置
    max_concurrent_handlers: int = int(os.getenv("EVENT_MAX_CONCURRENT_HANDLERS", "10"))
    handler_timeout_seconds: float = float(os.getenv("EVENT_HANDLER_TIMEOUT_SECONDS", "30.0"))
    
    # 清理配置
    cleanup_processed_events_after_days: int = int(os.getenv("EVENT_CLEANUP_AFTER_DAYS", "30"))
    cleanup_failed_events_after_days: int = int(os.getenv("EVENT_CLEANUP_FAILED_AFTER_DAYS", "7"))
    
    # 监控配置
    enable_metrics: bool = os.getenv("EVENT_ENABLE_METRICS", "true").lower() == "true"
    metrics_interval_seconds: int = int(os.getenv("EVENT_METRICS_INTERVAL_SECONDS", "60"))


@dataclass
class EventStoreConfig:
    """事件存储配置"""
    type: EventStoreType = EventStoreType(os.getenv("EVENT_STORE_TYPE", "sql"))
    
    # SQL 存储配置
    table_name: str = os.getenv("EVENT_STORE_TABLE_NAME", "domain_events")
    
    # 内存存储配置
    max_events_in_memory: int = int(os.getenv("EVENT_STORE_MAX_MEMORY_EVENTS", "10000"))
    
    # 查询配置
    default_page_size: int = int(os.getenv("EVENT_STORE_DEFAULT_PAGE_SIZE", "100"))
    max_page_size: int = int(os.getenv("EVENT_STORE_MAX_PAGE_SIZE", "1000"))


@dataclass
class EventPublisherConfig:
    """事件发布器配置"""
    type: EventPublisherType = EventPublisherType(os.getenv("EVENT_PUBLISHER_TYPE", "redis"))
    
    # 发布配置
    enable_async_publishing: bool = os.getenv("EVENT_ENABLE_ASYNC_PUBLISHING", "true").lower() == "true"
    publish_timeout_seconds: float = float(os.getenv("EVENT_PUBLISH_TIMEOUT_SECONDS", "5.0"))
    
    # 重试配置
    max_publish_retry_attempts: int = int(os.getenv("EVENT_MAX_PUBLISH_RETRY_ATTEMPTS", "3"))
    publish_retry_delay_seconds: float = float(os.getenv("EVENT_PUBLISH_RETRY_DELAY_SECONDS", "0.5"))


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = os.getenv(
        "LOG_FORMAT", 
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 事件特定日志配置
    log_event_publishing: bool = os.getenv("LOG_EVENT_PUBLISHING", "true").lower() == "true"
    log_event_handling: bool = os.getenv("LOG_EVENT_HANDLING", "true").lower() == "true"
    log_event_errors: bool = os.getenv("LOG_EVENT_ERRORS", "true").lower() == "true"
    log_performance_metrics: bool = os.getenv("LOG_PERFORMANCE_METRICS", "false").lower() == "true"


@dataclass
class SecurityConfig:
    """安全配置"""
    # 事件验证
    enable_event_validation: bool = os.getenv("EVENT_ENABLE_VALIDATION", "true").lower() == "true"
    max_event_size_bytes: int = int(os.getenv("EVENT_MAX_SIZE_BYTES", "1048576"))  # 1MB
    
    # 访问控制
    enable_access_control: bool = os.getenv("EVENT_ENABLE_ACCESS_CONTROL", "false").lower() == "true"
    allowed_event_types: Optional[str] = os.getenv("EVENT_ALLOWED_TYPES")  # 逗号分隔的事件类型
    
    # 加密
    enable_event_encryption: bool = os.getenv("EVENT_ENABLE_ENCRYPTION", "false").lower() == "true"
    encryption_key: Optional[str] = os.getenv("EVENT_ENCRYPTION_KEY")


@dataclass
class EventDrivenConfig:
    """事件驱动架构总配置"""
    # 环境配置
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 子配置
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    event_processing: EventProcessingConfig = EventProcessingConfig()
    event_store: EventStoreConfig = EventStoreConfig()
    event_publisher: EventPublisherConfig = EventPublisherConfig()
    logging: LoggingConfig = LoggingConfig()
    security: SecurityConfig = SecurityConfig()
    
    # 功能开关
    enable_event_replay: bool = os.getenv("EVENT_ENABLE_REPLAY", "true").lower() == "true"
    enable_event_history: bool = os.getenv("EVENT_ENABLE_HISTORY", "true").lower() == "true"
    enable_health_checks: bool = os.getenv("EVENT_ENABLE_HEALTH_CHECKS", "true").lower() == "true"
    
    # 性能配置
    enable_performance_monitoring: bool = os.getenv("EVENT_ENABLE_PERFORMANCE_MONITORING", "true").lower() == "true"
    slow_event_threshold_seconds: float = float(os.getenv("EVENT_SLOW_THRESHOLD_SECONDS", "1.0"))
    
    def get_allowed_event_types(self) -> Optional[list[str]]:
        """获取允许的事件类型列表"""
        if self.security.allowed_event_types:
            return [t.strip() for t in self.security.allowed_event_types.split(",")]
        return None
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment.lower() == "development"
    
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.environment.lower() in ["test", "testing"]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "database": {
                "url": self.database.url,
                "pool_size": self.database.pool_size,
                "max_overflow": self.database.max_overflow,
                "echo": self.database.echo
            },
            "redis": {
                "host": self.redis.host,
                "port": self.redis.port,
                "db": self.redis.db,
                "channel_prefix": self.redis.channel_prefix,
                "max_connections": self.redis.max_connections
            },
            "event_processing": {
                "max_retry_attempts": self.event_processing.max_retry_attempts,
                "batch_size": self.event_processing.batch_size,
                "max_concurrent_handlers": self.event_processing.max_concurrent_handlers
            },
            "features": {
                "enable_event_replay": self.enable_event_replay,
                "enable_event_history": self.enable_event_history,
                "enable_health_checks": self.enable_health_checks,
                "enable_performance_monitoring": self.enable_performance_monitoring
            }
        }


# 全局配置实例
config = EventDrivenConfig()


def get_config() -> EventDrivenConfig:
    """获取配置实例"""
    return config


def reload_config() -> EventDrivenConfig:
    """重新加载配置"""
    global config
    config = EventDrivenConfig()
    return config


def update_config(**kwargs) -> EventDrivenConfig:
    """更新配置"""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config