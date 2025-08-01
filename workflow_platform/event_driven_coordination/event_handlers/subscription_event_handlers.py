"""订阅事件处理器

处理订阅模块产生的事件，协调其他模块的响应
"""

import logging
from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime

from shared_kernel.domain.events.domain_event import DomainEvent, EventHandler


logger = logging.getLogger(__name__)


class SubscriptionActivationEventHandler(EventHandler):
    """订阅激活事件处理器
    
    当用户订阅被激活时，需要：
    1. 启用高级工作流功能
    2. 更新用户权限
    3. 发送激活确认邮件
    4. 记录订阅行为
    5. 触发欢迎工作流
    """
    
    @property
    def handled_event_types(self) -> List[str]:
        """处理的事件类型列表"""
        return ["SubscriptionActivated"]
    
    async def handle(self, event: DomainEvent) -> None:
        """处理订阅激活事件"""
        try:
            subscription_id = event.aggregate_id
            subscription_data = event.event_data
            user_id = subscription_data.get('user_id')
            plan_type = subscription_data.get('plan_type')
            
            logger.info(f"Processing subscription activation for user {user_id}, plan: {plan_type}")
            
            # 1. 启用高级工作流功能
            await self._enable_premium_workflows(user_id, plan_type, subscription_data)
            
            # 2. 更新用户权限
            await self._update_user_permissions(user_id, plan_type, subscription_data)
            
            # 3. 发送激活确认邮件
            await self._send_activation_email(user_id, subscription_data)
            
            # 4. 记录订阅行为
            await self._track_subscription_activation(user_id, subscription_data)
            
            # 5. 触发欢迎工作流
            await self._trigger_welcome_workflows(user_id, plan_type, subscription_data)
            
            logger.info(f"Successfully processed subscription activation for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to process subscription activation event: {str(e)}")
            raise
    
    async def _enable_premium_workflows(self, user_id: UUID, plan_type: str, subscription_data: Dict[str, Any]) -> None:
        """启用高级工作流功能"""
        try:
            logger.info(f"Enabling premium workflows for user {user_id}, plan: {plan_type}")
            
            # 根据订阅计划类型启用不同的工作流功能
            premium_features = self._get_premium_features_by_plan(plan_type)
            
            for feature in premium_features:
                logger.info(f"Enabling feature {feature} for user {user_id}")
                # TODO: 发布 EnableWorkflowFeatureEvent
                # await self.event_bus.publish(EnableWorkflowFeatureEvent(
                #     user_id=user_id,
                #     feature=feature,
                #     subscription_id=subscription_data.get('subscription_id')
                # ))
            
        except Exception as e:
            logger.error(f"Failed to enable premium workflows for user {user_id}: {str(e)}")
            raise
    
    async def _update_user_permissions(self, user_id: UUID, plan_type: str, subscription_data: Dict[str, Any]) -> None:
        """更新用户权限"""
        try:
            logger.info(f"Updating user permissions for user {user_id}, plan: {plan_type}")
            
            # 获取计划对应的权限
            permissions = self._get_permissions_by_plan(plan_type)
            
            # TODO: 发布 UpdateUserPermissionsEvent
            # await self.event_bus.publish(UpdateUserPermissionsEvent(
            #     user_id=user_id,
            #     permissions=permissions,
            #     subscription_id=subscription_data.get('subscription_id')
            # ))
            
        except Exception as e:
            logger.error(f"Failed to update user permissions for user {user_id}: {str(e)}")
            raise
    
    async def _send_activation_email(self, user_id: UUID, subscription_data: Dict[str, Any]) -> None:
        """发送激活确认邮件"""
        try:
            user_email = subscription_data.get('user_email')
            plan_type = subscription_data.get('plan_type')
            
            if user_email:
                logger.info(f"Sending activation email to {user_email}")
                
                # TODO: 发布 SendSubscriptionActivationEmailEvent
                # await self.event_bus.publish(SendSubscriptionActivationEmailEvent(
                #     user_id=user_id,
                #     email=user_email,
                #     plan_type=plan_type,
                #     subscription_data=subscription_data
                # ))
            
        except Exception as e:
            logger.error(f"Failed to send activation email for user {user_id}: {str(e)}")
            # 邮件发送失败不应该影响整个流程
    
    async def _track_subscription_activation(self, user_id: UUID, subscription_data: Dict[str, Any]) -> None:
        """记录订阅激活行为"""
        try:
            logger.info(f"Tracking subscription activation for user {user_id}")
            
            # TODO: 发布 SubscriptionBehaviorTrackingEvent
            # await self.event_bus.publish(SubscriptionBehaviorTrackingEvent(
            #     user_id=user_id,
            #     action='activation',
            #     subscription_data=subscription_data,
            #     timestamp=datetime.utcnow()
            # ))
            
        except Exception as e:
            logger.error(f"Failed to track subscription activation for user {user_id}: {str(e)}")
            # 行为追踪失败不应该影响整个流程
    
    async def _trigger_welcome_workflows(self, user_id: UUID, plan_type: str, subscription_data: Dict[str, Any]) -> None:
        """触发欢迎工作流"""
        try:
            logger.info(f"Triggering welcome workflows for user {user_id}, plan: {plan_type}")
            
            # TODO: 发布 TriggerWelcomeWorkflowsEvent
            # await self.event_bus.publish(TriggerWelcomeWorkflowsEvent(
            #     user_id=user_id,
            #     plan_type=plan_type,
            #     subscription_data=subscription_data
            # ))
            
        except Exception as e:
            logger.error(f"Failed to trigger welcome workflows for user {user_id}: {str(e)}")
            # 工作流触发失败不应该影响整个流程
    
    def _get_premium_features_by_plan(self, plan_type: str) -> list:
        """根据订阅计划获取高级功能列表"""
        feature_mapping = {
            'basic': ['basic_automation'],
            'premium': ['basic_automation', 'advanced_automation', 'custom_workflows'],
            'enterprise': ['basic_automation', 'advanced_automation', 'custom_workflows', 'api_access', 'priority_support']
        }
        return feature_mapping.get(plan_type, [])
    
    def _get_permissions_by_plan(self, plan_type: str) -> list:
        """根据订阅计划获取权限列表"""
        permission_mapping = {
            'basic': ['workflow:read', 'workflow:execute'],
            'premium': ['workflow:read', 'workflow:execute', 'workflow:create', 'workflow:edit'],
            'enterprise': ['workflow:read', 'workflow:execute', 'workflow:create', 'workflow:edit', 'workflow:admin', 'api:access']
        }
        return permission_mapping.get(plan_type, [])


class SubscriptionExpirationEventHandler(EventHandler):
    """订阅过期事件处理器
    
    当用户订阅过期时，需要：
    1. 禁用高级工作流功能
    2. 降级用户权限
    3. 发送过期通知邮件
    4. 暂停正在运行的高级工作流
    5. 记录过期行为
    """
    
    @property
    def handled_event_types(self) -> List[str]:
        """处理的事件类型列表"""
        return ["SubscriptionExpired"]
    
    async def handle(self, event: DomainEvent) -> None:
        """处理订阅过期事件"""
        try:
            subscription_id = event.aggregate_id
            subscription_data = event.event_data
            user_id = subscription_data.get('user_id')
            expired_plan = subscription_data.get('plan_type')
            
            logger.info(f"Processing subscription expiration for user {user_id}, expired plan: {expired_plan}")
            
            # 1. 禁用高级工作流功能
            await self._disable_premium_workflows(user_id, expired_plan, subscription_data)
            
            # 2. 降级用户权限
            await self._downgrade_user_permissions(user_id, subscription_data)
            
            # 3. 发送过期通知邮件
            await self._send_expiration_email(user_id, subscription_data)
            
            # 4. 暂停正在运行的高级工作流
            await self._suspend_premium_workflows(user_id, expired_plan, subscription_data)
            
            # 5. 记录过期行为
            await self._track_subscription_expiration(user_id, subscription_data)
            
            logger.info(f"Successfully processed subscription expiration for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to process subscription expiration event: {str(e)}")
            raise
    
    async def _disable_premium_workflows(self, user_id: UUID, expired_plan: str, subscription_data: Dict[str, Any]) -> None:
        """禁用高级工作流功能"""
        try:
            logger.info(f"Disabling premium workflows for user {user_id}, expired plan: {expired_plan}")
            
            # 获取需要禁用的高级功能
            premium_features = self._get_premium_features_by_plan(expired_plan)
            
            for feature in premium_features:
                logger.info(f"Disabling feature {feature} for user {user_id}")
                # TODO: 发布 DisableWorkflowFeatureEvent
                # await self.event_bus.publish(DisableWorkflowFeatureEvent(
                #     user_id=user_id,
                #     feature=feature,
                #     reason='subscription_expired'
                # ))
            
        except Exception as e:
            logger.error(f"Failed to disable premium workflows for user {user_id}: {str(e)}")
            raise
    
    async def _downgrade_user_permissions(self, user_id: UUID, subscription_data: Dict[str, Any]) -> None:
        """降级用户权限到基础版"""
        try:
            logger.info(f"Downgrading user permissions for user {user_id}")
            
            # 降级到基础权限
            basic_permissions = self._get_permissions_by_plan('basic')
            
            # TODO: 发布 UpdateUserPermissionsEvent
            # await self.event_bus.publish(UpdateUserPermissionsEvent(
            #     user_id=user_id,
            #     permissions=basic_permissions,
            #     reason='subscription_expired'
            # ))
            
        except Exception as e:
            logger.error(f"Failed to downgrade user permissions for user {user_id}: {str(e)}")
            raise
    
    async def _send_expiration_email(self, user_id: UUID, subscription_data: Dict[str, Any]) -> None:
        """发送过期通知邮件"""
        try:
            user_email = subscription_data.get('user_email')
            expired_plan = subscription_data.get('plan_type')
            
            if user_email:
                logger.info(f"Sending expiration email to {user_email}")
                
                # TODO: 发布 SendSubscriptionExpirationEmailEvent
                # await self.event_bus.publish(SendSubscriptionExpirationEmailEvent(
                #     user_id=user_id,
                #     email=user_email,
                #     expired_plan=expired_plan,
                #     subscription_data=subscription_data
                # ))
            
        except Exception as e:
            logger.error(f"Failed to send expiration email for user {user_id}: {str(e)}")
            # 邮件发送失败不应该影响整个流程
    
    async def _suspend_premium_workflows(self, user_id: UUID, expired_plan: str, subscription_data: Dict[str, Any]) -> None:
        """暂停正在运行的高级工作流"""
        try:
            logger.info(f"Suspending premium workflows for user {user_id}")
            
            # TODO: 发布 SuspendPremiumWorkflowsEvent
            # await self.event_bus.publish(SuspendPremiumWorkflowsEvent(
            #     user_id=user_id,
            #     expired_plan=expired_plan,
            #     reason='subscription_expired'
            # ))
            
        except Exception as e:
            logger.error(f"Failed to suspend premium workflows for user {user_id}: {str(e)}")
            raise
    
    async def _track_subscription_expiration(self, user_id: UUID, subscription_data: Dict[str, Any]) -> None:
        """记录订阅过期行为"""
        try:
            logger.info(f"Tracking subscription expiration for user {user_id}")
            
            # TODO: 发布 SubscriptionBehaviorTrackingEvent
            # await self.event_bus.publish(SubscriptionBehaviorTrackingEvent(
            #     user_id=user_id,
            #     action='expiration',
            #     subscription_data=subscription_data,
            #     timestamp=datetime.utcnow()
            # ))
            
        except Exception as e:
            logger.error(f"Failed to track subscription expiration for user {user_id}: {str(e)}")
            # 行为追踪失败不应该影响整个流程
    
    def _get_premium_features_by_plan(self, plan_type: str) -> list:
        """根据订阅计划获取高级功能列表"""
        feature_mapping = {
            'basic': [],
            'premium': ['advanced_automation', 'custom_workflows'],
            'enterprise': ['advanced_automation', 'custom_workflows', 'api_access', 'priority_support']
        }
        return feature_mapping.get(plan_type, [])
    
    def _get_permissions_by_plan(self, plan_type: str) -> list:
        """根据订阅计划获取权限列表"""
        permission_mapping = {
            'basic': ['workflow:read', 'workflow:execute']
        }
        return permission_mapping.get(plan_type, [])