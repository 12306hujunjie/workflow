"""应用配置"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = "Workflow Platform"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # 数据库配置
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/workflow_platform",
        env="DATABASE_URL"
    )
    db_echo: bool = Field(default=False, env="DB_ECHO")
    
    # Redis配置
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # JWT配置
    jwt_secret_key: str = Field(default=None, env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # 密码加密配置
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")
    
    # CORS配置
    cors_allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"],
        env="CORS_ALLOWED_ORIGINS"
    )
    
    # 邮件配置
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_from_email: Optional[str] = Field(default=None, env="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="Workflow Platform", env="SMTP_FROM_NAME")
    
    # Prefect配置
    prefect_api_url: Optional[str] = Field(default=None, env="PREFECT_API_URL")
    prefect_api_key: Optional[str] = Field(default=None, env="PREFECT_API_KEY")
    
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings