"""邮件服务基础设施"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """邮件配置"""
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool = True
    from_email: str = None
    from_name: str = "智能工作流管理平台"
    
    def __post_init__(self):
        if not self.from_email:
            self.from_email = self.smtp_username


class EmailService(ABC):
    """邮件服务抽象基类"""
    
    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """发送邮件"""
        pass
    
    @abstractmethod
    async def send_verification_email(self, to_email: str, username: str, token: str) -> bool:
        """发送邮箱验证邮件"""
        pass
    
    @abstractmethod
    async def send_password_reset_email(self, to_email: str, username: str, token: str) -> bool:
        """发送密码重置邮件"""
        pass


class SMTPEmailService(EmailService):
    """SMTP邮件服务实现"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """发送邮件"""
        try:
            # 在线程池中运行SMTP操作，避免阻塞异步事件循环
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, 
                self._send_smtp_email,
                to_email, subject, html_content, text_content
            )
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            return False
    
    def _send_smtp_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """同步发送SMTP邮件"""
        try:
            # 创建邮件消息
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = to_email
            
            # 添加文本内容
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.smtp_use_tls:
                    server.starttls()
                
                server.login(self.config.smtp_username, self.config.smtp_password)
                server.send_message(msg)
            
            logger.info(f"邮件发送成功: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP邮件发送失败: {str(e)}")
            return False
    
    async def send_verification_email(self, to_email: str, username: str, token: str) -> bool:
        """发送邮箱验证邮件"""
        # 构建验证链接
        verify_url = f"http://localhost:5173/auth/verify-email?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>邮箱验证</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1890ff;">邮箱验证</h2>
                <p>亲爱的 {username}，</p>
                <p>欢迎注册智能工作流管理平台！请点击下面的链接验证您的邮箱地址：</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verify_url}" 
                       style="display: inline-block; background-color: #1890ff; color: white; 
                              padding: 12px 30px; text-decoration: none; border-radius: 5px;">
                        验证邮箱
                    </a>
                </div>
                <p>如果上述按钮无法点击，请复制以下链接到浏览器地址栏：</p>
                <p style="word-break: break-all; background: #f5f5f5; padding: 10px; border-radius: 3px;">
                    {verify_url}
                </p>
                <p style="color: #999; font-size: 12px;">
                    此链接将在24小时后过期。如果您没有注册此账户，请忽略此邮件。
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        邮箱验证
        
        亲爱的 {username}，
        
        欢迎注册智能工作流管理平台！请访问以下链接验证您的邮箱地址：
        
        {verify_url}
        
        此链接将在24小时后过期。如果您没有注册此账户，请忽略此邮件。
        """
        
        return await self.send_email(to_email, "邮箱验证 - 智能工作流管理平台", html_content, text_content)
    
    async def send_password_reset_email(self, to_email: str, username: str, token: str) -> bool:
        """发送密码重置邮件"""
        # 构建重置链接
        reset_url = f"http://localhost:5173/auth/reset-password?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>密码重置</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #ff4d4f;">密码重置</h2>
                <p>亲爱的 {username}，</p>
                <p>我们收到了您的密码重置请求。请点击下面的链接重置您的密码：</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="display: inline-block; background-color: #ff4d4f; color: white; 
                              padding: 12px 30px; text-decoration: none; border-radius: 5px;">
                        重置密码
                    </a>
                </div>
                <p>如果上述按钮无法点击，请复制以下链接到浏览器地址栏：</p>
                <p style="word-break: break-all; background: #f5f5f5; padding: 10px; border-radius: 3px;">
                    {reset_url}
                </p>
                <p style="color: #999; font-size: 12px;">
                    此链接将在1小时后过期。如果您没有请求重置密码，请忽略此邮件。
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        密码重置
        
        亲爱的 {username}，
        
        我们收到了您的密码重置请求。请访问以下链接重置您的密码：
        
        {reset_url}
        
        此链接将在1小时后过期。如果您没有请求重置密码，请忽略此邮件。
        """
        
        return await self.send_email(to_email, "密码重置 - 智能工作流管理平台", html_content, text_content)


class MockEmailService(EmailService):
    """模拟邮件服务 - 用于开发和测试"""
    
    def __init__(self):
        self.sent_emails = []
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """模拟发送邮件"""
        email_data = {
            "to_email": to_email,
            "subject": subject,
            "html_content": html_content,
            "text_content": text_content,
            "sent_at": asyncio.get_event_loop().time()
        }
        
        self.sent_emails.append(email_data)
        logger.info(f"[MOCK] 邮件已发送到 {to_email}: {subject}")
        return True
    
    async def send_verification_email(self, to_email: str, username: str, token: str) -> bool:
        """模拟发送邮箱验证邮件"""
        verify_url = f"http://localhost:5173/auth/verify-email?token={token}"
        html_content = f"验证链接: {verify_url}"
        
        logger.info(f"[MOCK] 邮箱验证邮件发送到 {to_email}")
        logger.info(f"[MOCK] 验证链接: {verify_url}")
        
        return await self.send_email(to_email, "邮箱验证", html_content)
    
    async def send_password_reset_email(self, to_email: str, username: str, token: str) -> bool:
        """模拟发送密码重置邮件"""
        reset_url = f"http://localhost:5173/auth/reset-password?token={token}"
        html_content = f"重置链接: {reset_url}"
        
        logger.info(f"[MOCK] 密码重置邮件发送到 {to_email}")
        logger.info(f"[MOCK] 重置链接: {reset_url}")
        
        return await self.send_email(to_email, "密码重置", html_content)