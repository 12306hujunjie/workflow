from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio
import logging


class NotificationType(Enum):
    """通知类型枚举"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    PUSH = "push"


class NotificationPriority(Enum):
    """通知优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(Enum):
    """通知状态枚举"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"


@dataclass
class NotificationMessage:
    """通知消息"""
    id: str
    recipient: str  # 接收者（邮箱、手机号、用户ID等）
    notification_type: NotificationType
    title: str
    content: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    metadata: Dict[str, Any] = None
    scheduled_at: Optional[datetime] = None
    created_at: datetime = None
    status: NotificationStatus = NotificationStatus.PENDING
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class NotificationChannel(ABC):
    """通知渠道接口"""
    
    @property
    @abstractmethod
    def channel_type(self) -> NotificationType:
        pass
    
    @abstractmethod
    async def send(self, message: NotificationMessage) -> bool:
        """发送通知，返回是否成功"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """检查渠道是否可用"""
        pass


class NotificationRepository(ABC):
    """通知仓储接口"""
    
    @abstractmethod
    async def save(self, message: NotificationMessage) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, message_id: str) -> Optional[NotificationMessage]:
        pass
    
    @abstractmethod
    async def find_pending_messages(self, limit: int = 100) -> List[NotificationMessage]:
        pass
    
    @abstractmethod
    async def find_by_recipient(self, recipient: str, limit: int = 50) -> List[NotificationMessage]:
        pass
    
    @abstractmethod
    async def update_status(self, message_id: str, status: NotificationStatus, 
                           error_message: Optional[str] = None) -> None:
        pass


class NotificationService:
    """通知服务"""
    
    def __init__(self, repository: NotificationRepository):
        self.repository = repository
        self.channels: Dict[NotificationType, NotificationChannel] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_channel(self, channel: NotificationChannel):
        """注册通知渠道"""
        self.channels[channel.channel_type] = channel
        self.logger.info(f"Registered notification channel: {channel.channel_type.value}")
    
    async def send_notification(self, message: NotificationMessage) -> bool:
        """发送单个通知"""
        try:
            # 保存通知记录
            await self.repository.save(message)
            
            # 检查是否需要延迟发送
            if message.scheduled_at and message.scheduled_at > datetime.utcnow():
                self.logger.info(f"Notification {message.id} scheduled for {message.scheduled_at}")
                return True
            
            # 获取对应的通知渠道
            channel = self.channels.get(message.notification_type)
            if not channel:
                error_msg = f"No channel registered for {message.notification_type.value}"
                self.logger.error(error_msg)
                await self.repository.update_status(message.id, NotificationStatus.FAILED, error_msg)
                return False
            
            # 检查渠道是否可用
            if not await channel.is_available():
                error_msg = f"Channel {message.notification_type.value} is not available"
                self.logger.warning(error_msg)
                await self.repository.update_status(message.id, NotificationStatus.FAILED, error_msg)
                return False
            
            # 发送通知
            success = await channel.send(message)
            
            if success:
                message.status = NotificationStatus.SENT
                message.sent_at = datetime.utcnow()
                await self.repository.update_status(message.id, NotificationStatus.SENT)
                self.logger.info(f"Notification {message.id} sent successfully")
                return True
            else:
                message.retry_count += 1
                if message.retry_count >= message.max_retries:
                    await self.repository.update_status(message.id, NotificationStatus.FAILED, "Max retries exceeded")
                    self.logger.error(f"Notification {message.id} failed after {message.max_retries} retries")
                else:
                    self.logger.warning(f"Notification {message.id} failed, retry {message.retry_count}/{message.max_retries}")
                return False
        
        except Exception as e:
            error_msg = f"Error sending notification {message.id}: {str(e)}"
            self.logger.error(error_msg)
            await self.repository.update_status(message.id, NotificationStatus.FAILED, error_msg)
            return False
    
    async def send_bulk_notifications(self, messages: List[NotificationMessage]) -> Dict[str, bool]:
        """批量发送通知"""
        results = {}
        
        # 按通知类型分组
        grouped_messages = {}
        for message in messages:
            if message.notification_type not in grouped_messages:
                grouped_messages[message.notification_type] = []
            grouped_messages[message.notification_type].append(message)
        
        # 并发发送不同类型的通知
        tasks = []
        for notification_type, type_messages in grouped_messages.items():
            for message in type_messages:
                task = asyncio.create_task(self.send_notification(message))
                tasks.append((message.id, task))
        
        # 等待所有任务完成
        for message_id, task in tasks:
            try:
                result = await task
                results[message_id] = result
            except Exception as e:
                self.logger.error(f"Error in bulk send for message {message_id}: {str(e)}")
                results[message_id] = False
        
        return results
    
    async def process_pending_notifications(self):
        """处理待发送的通知"""
        try:
            pending_messages = await self.repository.find_pending_messages()
            
            if not pending_messages:
                return
            
            self.logger.info(f"Processing {len(pending_messages)} pending notifications")
            
            # 过滤出需要立即发送的通知
            immediate_messages = []
            for message in pending_messages:
                if not message.scheduled_at or message.scheduled_at <= datetime.utcnow():
                    immediate_messages.append(message)
            
            if immediate_messages:
                results = await self.send_bulk_notifications(immediate_messages)
                success_count = sum(1 for success in results.values() if success)
                self.logger.info(f"Processed {len(immediate_messages)} notifications, {success_count} successful")
        
        except Exception as e:
            self.logger.error(f"Error processing pending notifications: {str(e)}")
    
    async def retry_failed_notifications(self):
        """重试失败的通知"""
        try:
            # 这里需要从仓储中获取失败但还可以重试的通知
            # 为简化，我们假设有这样的方法
            # failed_messages = await self.repository.find_retryable_failed_messages()
            
            # 实际实现中，你需要在仓储中添加这个方法
            pass
        
        except Exception as e:
            self.logger.error(f"Error retrying failed notifications: {str(e)}")
    
    async def get_notification_stats(self) -> Dict[str, Any]:
        """获取通知统计信息"""
        # 这里需要在仓储中实现统计方法
        # 为简化，返回基本信息
        return {
            "registered_channels": list(self.channels.keys()),
            "total_channels": len(self.channels)
        }
    
    async def mark_as_delivered(self, message_id: str):
        """标记通知为已送达"""
        message = await self.repository.find_by_id(message_id)
        if message:
            message.status = NotificationStatus.DELIVERED
            message.delivered_at = datetime.utcnow()
            await self.repository.update_status(message_id, NotificationStatus.DELIVERED)
    
    async def mark_as_read(self, message_id: str):
        """标记通知为已读"""
        await self.repository.update_status(message_id, NotificationStatus.READ)


class NotificationTemplate:
    """通知模板"""
    
    def __init__(self, template_id: str, title_template: str, content_template: str):
        self.template_id = template_id
        self.title_template = title_template
        self.content_template = content_template
    
    def render(self, variables: Dict[str, Any]) -> tuple[str, str]:
        """渲染模板，返回(title, content)"""
        title = self.title_template.format(**variables)
        content = self.content_template.format(**variables)
        return title, content


class NotificationTemplateManager:
    """通知模板管理器"""
    
    def __init__(self):
        self.templates: Dict[str, NotificationTemplate] = {}
    
    def register_template(self, template: NotificationTemplate):
        """注册模板"""
        self.templates[template.template_id] = template
    
    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """获取模板"""
        return self.templates.get(template_id)
    
    def render_notification(self, template_id: str, variables: Dict[str, Any]) -> Optional[tuple[str, str]]:
        """渲染通知内容"""
        template = self.get_template(template_id)
        if template:
            return template.render(variables)
        return None