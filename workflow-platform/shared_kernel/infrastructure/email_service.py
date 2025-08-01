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
    async def send_verification_code_email(self, to_email: str, username: str, code: str, purpose: str) -> bool:
        """发送验证码邮件"""
        pass
    
    # 保持兼容性的旧方法
    async def send_verification_email(self, to_email: str, username: str, token: str) -> bool:
        """发送邮箱验证邮件（兼容性方法）"""
        return await self.send_verification_code_email(to_email, username, token, "register")
    
    async def send_password_reset_email(self, to_email: str, username: str, token: str) -> bool:
        """发送密码重置邮件（兼容性方法）"""
        return await self.send_verification_code_email(to_email, username, token, "reset_password")


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
            # QQ Mail requires simple From format for compliance
            msg['From'] = self.config.from_email
            msg['To'] = to_email
            
            # 添加文本内容
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件
            server = smtplib.SMTP(self.config.smtp_host, self.config.smtp_port)
            try:
                if self.config.smtp_use_tls:
                    server.starttls()
                
                server.login(self.config.smtp_username, self.config.smtp_password)
                server.send_message(msg)
                
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP认证失败: {str(e)}")
                raise
            except smtplib.SMTPException as e:
                logger.error(f"SMTP错误: {str(e)}")
                raise
            finally:
                try:
                    server.quit()
                except:
                    # Ignore cleanup errors
                    pass
            
            logger.info(f"邮件发送成功: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP邮件发送失败: {str(e)}")
            return False
    
    async def send_verification_code_email(self, to_email: str, username: str, code: str, purpose: str) -> bool:
        """发送验证码邮件"""
        # 根据用途设置邮件内容
        if purpose == "register":
            subject = "邮箱验证码 - 智能工作流管理平台"
            purpose_text = "注册账户"
            action_text = "完成注册"
        elif purpose == "reset_password":
            subject = "密码重置验证码 - 智能工作流管理平台"
            purpose_text = "重置密码"
            action_text = "重置密码"
        else:
            subject = "验证码 - 智能工作流管理平台"
            purpose_text = "验证身份"
            action_text = "继续操作"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{subject}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #1890ff; margin: 0; font-size: 24px;">智能工作流管理平台</h1>
                </div>
                
                <h2 style="color: #333; text-align: center; margin-bottom: 20px;">{purpose_text}验证码</h2>
                
                <p style="font-size: 16px;">尊敬的 <strong>{username}</strong>，</p>
                
                <p style="font-size: 16px;">您正在{purpose_text}，请使用以下验证码{action_text}：</p>
                
                <div style="text-align: center; margin: 40px 0;">
                    <div style="display: inline-block; background-color: #f0f8ff; border: 2px dashed #1890ff; border-radius: 8px; padding: 20px 40px;">
                        <span style="font-size: 32px; font-weight: bold; color: #1890ff; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                            {code}
                        </span>
                    </div>
                </div>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404; font-size: 14px;">
                        <strong>安全提醒：</strong>
                        <br>• 验证码有效期为 <strong>5分钟</strong>
                        <br>• 验证码仅可使用 <strong>一次</strong>
                        <br>• 请勿向他人泄露验证码
                    </p>
                </div>
                
                <p style="color: #999; font-size: 12px; text-align: center; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                    如果您没有进行此操作，请忽略此邮件。此验证码将在5分钟后自动失效。
                    <br>
                    © 2024 智能工作流管理平台 保留所有权利
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
智能工作流管理平台 - {purpose_text}验证码

尊敬的 {username}，

您正在{purpose_text}，请使用以下验证码{action_text}：

验证码：{code}

安全提醒：
• 验证码有效期为5分钟
• 验证码仅可使用一次
• 请勿向他人泄露验证码

如果您没有进行此操作，请忽略此邮件。

© 2024 智能工作流管理平台
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    # 老的方法保留，用于兼容性
    async def send_verification_email(self, to_email: str, username: str, token: str) -> bool:
        """发送邮箱验证邮件（兼容性方法）"""
        return await self.send_verification_code_email(to_email, username, token, "register")
    
    async def send_password_reset_email(self, to_email: str, username: str, token: str) -> bool:
        """发送密码重置邮件（兼容性方法）"""
        return await self.send_verification_code_email(to_email, username, token, "reset_password")


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
    
    async def send_verification_code_email(self, to_email: str, username: str, code: str, purpose: str) -> bool:
        """模拟发送验证码邮件"""
        logger.info(f"[MOCK] 验证码邮件发送到 {to_email}")
        logger.info(f"[MOCK] 用户: {username}, 验证码: {code}, 用途: {purpose}")
        
        subject = f"验证码 - {purpose}"
        html_content = f"验证码: {code} (用途: {purpose})"
        
        return await self.send_email(to_email, subject, html_content)
    
    # 兼容性方法
    async def send_verification_email(self, to_email: str, username: str, token: str) -> bool:
        """模拟发送邮箱验证邮件（兼容性方法）"""
        return await self.send_verification_code_email(to_email, username, token, "register")
    
    async def send_password_reset_email(self, to_email: str, username: str, token: str) -> bool:
        """模拟发送密码重置邮件（兼容性方法）"""
        return await self.send_verification_code_email(to_email, username, token, "reset_password")