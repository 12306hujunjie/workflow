"""用户事件处理器

处理用户管理模块产生的事件，协调其他模块的响应
"""

import logging
from typing import Dict, Any, List
from uuid import UUID

from shared_kernel.domain.events.domain_event import DomainEvent, EventHandler


logger = logging.getLogger(__name__)


class UserRegistrationEventHandler(EventHandler):
    """用户注册事件处理器
    
    当用户注册时，需要：
    1. 初始化用户的订阅状态
    2. 创建用户的工作流配置
    3. 发送欢迎邮件
    4. 记录用户行为分析
    """
    
    @property
    def handled_event_types(self) -> List[str]:
        """处理的事件类型列表"""
        return ["UserRegistered"]
    
    async def handle(self, event: DomainEvent) -> None:
        """处理用户注册事件"""
        try:
            user_id = event.aggregate_id
            user_data = event.event_data
            
            logger.info(f"Processing user registration for user {user_id}")
            
            # 1. 初始化订阅状态
            await self._initialize_subscription(user_id, user_data)
            
            # 2. 创建默认工作流配置
            await self._create_default_workflows(user_id, user_data)
            
            # 3. 发送欢迎邮件
            await self._send_welcome_email(user_id, user_data)
            
            # 4. 记录用户行为
            await self._track_user_registration(user_id, user_data)
            
            logger.info(f"Successfully processed user registration for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to process user registration event: {str(e)}")
            raise
    
    async def _initialize_subscription(self, user_id: UUID, user_data: Dict[str, Any]) -> None:
        """初始化用户订阅状态"""
        try:
            # 这里应该调用订阅模块的服务来初始化订阅
            # 为了避免直接依赖，我们通过事件总线发布新事件
            logger.info(f"Initializing subscription for user {user_id}")
            
            # TODO: 发布 InitializeSubscriptionEvent
            # await self.event_bus.publish(InitializeSubscriptionEvent(...))
            
        except Exception as e:
            logger.error(f"Failed to initialize subscription for user {user_id}: {str(e)}")
            raise
    
    async def _create_default_workflows(self, user_id: UUID, user_data: Dict[str, Any]) -> None:
        """创建默认工作流配置"""
        try:
            logger.info(f"Creating default workflows for user {user_id}")
            
            # TODO: 发布 CreateDefaultWorkflowsEvent
            # await self.event_bus.publish(CreateDefaultWorkflowsEvent(...))
            
        except Exception as e:
            logger.error(f"Failed to create default workflows for user {user_id}: {str(e)}")
            raise
    
    async def _send_welcome_email(self, user_id: UUID, user_data: Dict[str, Any]) -> None:
        """发送欢迎邮件"""
        try:
            email = user_data.get('email')
            if email:
                logger.info(f"Sending welcome email to {email}")
                
                # TODO: 发布 SendWelcomeEmailEvent
                # await self.event_bus.publish(SendWelcomeEmailEvent(...))
            
        except Exception as e:
            logger.error(f"Failed to send welcome email for user {user_id}: {str(e)}")
            # 邮件发送失败不应该影响整个流程
    
    async def _track_user_registration(self, user_id: UUID, user_data: Dict[str, Any]) -> None:
        """记录用户注册行为"""
        try:
            logger.info(f"Tracking user registration for user {user_id}")
            
            # TODO: 发布 UserBehaviorTrackingEvent
            # await self.event_bus.publish(UserBehaviorTrackingEvent(...))
            
        except Exception as e:
            logger.error(f"Failed to track user registration for user {user_id}: {str(e)}")
            # 行为追踪失败不应该影响整个流程


class UserStatusChangeEventHandler(EventHandler):
    """用户状态变更事件处理器
    
    当用户状态发生变化时（激活、禁用、删除等），需要：
    1. 更新订阅状态
    2. 暂停或恢复工作流
    3. 发送通知
    4. 更新权限
    """
    
    @property
    def handled_event_types(self) -> List[str]:
        """处理的事件类型列表"""
        return ["UserStatusChanged"]
    
    async def handle(self, event: DomainEvent) -> None:
        """处理用户状态变更事件"""
        try:
            user_id = event.aggregate_id
            event_data = event.event_data
            old_status = event_data.get('old_status')
            new_status = event_data.get('new_status')
            
            logger.info(f"Processing user status change for user {user_id}: {old_status} -> {new_status}")
            
            # 根据状态变化执行不同的处理逻辑
            if new_status == 'disabled':
                await self._handle_user_disabled(user_id, event_data)
            elif new_status == 'active' and old_status == 'disabled':
                await self._handle_user_reactivated(user_id, event_data)
            elif new_status == 'deleted':
                await self._handle_user_deleted(user_id, event_data)
            
            logger.info(f"Successfully processed user status change for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to process user status change event: {str(e)}")
            raise
    
    async def _handle_user_disabled(self, user_id: UUID, event_data: Dict[str, Any]) -> None:
        """处理用户禁用"""
        logger.info(f"Handling user disabled for user {user_id}")
        
        # 暂停所有工作流
        # TODO: 发布 SuspendUserWorkflowsEvent
        
        # 暂停订阅
        # TODO: 发布 SuspendUserSubscriptionEvent
        
        # 发送通知
        # TODO: 发布 SendUserStatusNotificationEvent
    
    async def _handle_user_reactivated(self, user_id: UUID, event_data: Dict[str, Any]) -> None:
        """处理用户重新激活"""
        logger.info(f"Handling user reactivated for user {user_id}")
        
        # 恢复工作流
        # TODO: 发布 ResumeUserWorkflowsEvent
        
        # 恢复订阅
        # TODO: 发布 ResumeUserSubscriptionEvent
    
    async def _handle_user_deleted(self, user_id: UUID, event_data: Dict[str, Any]) -> None:
        """处理用户删除"""
        logger.info(f"Handling user deleted for user {user_id}")
        
        # 删除所有工作流
        # TODO: 发布 DeleteUserWorkflowsEvent
        
        # 取消订阅
        # TODO: 发布 CancelUserSubscriptionEvent
        
        # 清理用户数据
        # TODO: 发布 CleanupUserDataEvent


class UserLoginEventHandler(EventHandler):
    """用户登录事件处理器
    
    当用户登录时，需要：
    1. 更新最后登录时间
    2. 检查账号安全
    3. 记录登录行为
    4. 触发相关工作流
    """
    
    @property
    def handled_event_types(self) -> List[str]:
        """处理的事件类型列表"""
        return ["UserLoggedIn"]
    
    async def handle(self, event: DomainEvent) -> None:
        """处理用户登录事件"""
        try:
            user_id = event.aggregate_id
            login_data = event.event_data
            
            logger.info(f"Processing user login for user {user_id}")
            
            # 1. 检查账号安全
            await self._check_account_security(user_id, login_data)
            
            # 2. 记录登录行为
            await self._track_login_behavior(user_id, login_data)
            
            # 3. 触发登录后工作流
            await self._trigger_post_login_workflows(user_id, login_data)
            
            logger.info(f"Successfully processed user login for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to process user login event: {str(e)}")
            raise
    
    async def _check_account_security(self, user_id: UUID, login_data: Dict[str, Any]) -> None:
        """检查账号安全"""
        try:
            ip_address = login_data.get('ip_address')
            user_agent = login_data.get('user_agent')
            
            logger.info(f"Checking account security for user {user_id} from IP {ip_address}")
            
            # TODO: 发布 AccountSecurityCheckEvent
            # await self.event_bus.publish(AccountSecurityCheckEvent(...))
            
        except Exception as e:
            logger.error(f"Failed to check account security for user {user_id}: {str(e)}")
            # 安全检查失败不应该阻止登录流程
    
    async def _track_login_behavior(self, user_id: UUID, login_data: Dict[str, Any]) -> None:
        """记录登录行为"""
        try:
            logger.info(f"Tracking login behavior for user {user_id}")
            
            # TODO: 发布 UserLoginBehaviorEvent
            # await self.event_bus.publish(UserLoginBehaviorEvent(...))
            
        except Exception as e:
            logger.error(f"Failed to track login behavior for user {user_id}: {str(e)}")
            # 行为追踪失败不应该影响登录流程
    
    async def _trigger_post_login_workflows(self, user_id: UUID, login_data: Dict[str, Any]) -> None:
        """触发登录后工作流"""
        try:
            logger.info(f"Triggering post-login workflows for user {user_id}")
            
            # TODO: 发布 TriggerPostLoginWorkflowsEvent
            # await self.event_bus.publish(TriggerPostLoginWorkflowsEvent(...))
            
        except Exception as e:
            logger.error(f"Failed to trigger post-login workflows for user {user_id}: {str(e)}")
            # 工作流触发失败不应该影响登录流程