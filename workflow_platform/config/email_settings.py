"""邮件服务配置"""

import os
from dataclasses import dataclass
from typing import Optional

from shared_kernel.infrastructure.email_service import EmailConfig


@dataclass
class EmailSettings:
    """邮件设置"""
    
    # 开发环境默认使用模拟邮件服务
    USE_MOCK_EMAIL: bool = True
    
    # SMTP服务器配置 - 生产环境需要配置
    SMTP_HOST: str = "smtp.163.com"  # 示例：网易邮箱
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""  # 发件人邮箱
    SMTP_PASSWORD: str = ""  # 邮箱密码或授权码
    SMTP_USE_TLS: bool = True
    
    # 发件人信息
    FROM_EMAIL: Optional[str] = None  # 如果为空，使用SMTP_USERNAME
    FROM_NAME: str = "智能工作流管理平台"
    
    # 前端URL配置
    FRONTEND_BASE_URL: str = "http://localhost:5173"
    
    @classmethod
    def from_env(cls) -> 'EmailSettings':
        """从环境变量加载配置"""
        return cls(
            USE_MOCK_EMAIL=os.getenv("EMAIL_USE_MOCK", "true").lower() == "true",
            SMTP_HOST=os.getenv("SMTP_HOST", "smtp.163.com"),
            SMTP_PORT=int(os.getenv("SMTP_PORT", "587")),
            SMTP_USERNAME=os.getenv("SMTP_USERNAME", ""),
            SMTP_PASSWORD=os.getenv("SMTP_PASSWORD", ""),
            SMTP_USE_TLS=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
            FROM_EMAIL=os.getenv("FROM_EMAIL"),
            FROM_NAME=os.getenv("FROM_NAME", "智能工作流管理平台"),
            FRONTEND_BASE_URL=os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
        )
    
    def to_email_config(self) -> EmailConfig:
        """转换为邮件服务配置"""
        return EmailConfig(
            smtp_host=self.SMTP_HOST,
            smtp_port=self.SMTP_PORT,
            smtp_username=self.SMTP_USERNAME,
            smtp_password=self.SMTP_PASSWORD,
            smtp_use_tls=self.SMTP_USE_TLS,
            from_email=self.FROM_EMAIL,
            from_name=self.FROM_NAME
        )


# 全局邮件设置实例
email_settings = EmailSettings.from_env()