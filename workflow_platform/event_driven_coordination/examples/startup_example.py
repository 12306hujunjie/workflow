"""事件驱动架构启动示例

展示如何在应用启动时初始化和配置事件驱动架构
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from event_driven_coordination import (
    get_coordinator,
    shutdown_coordinator,
    publish_event
)
from shared_kernel.domain.events.domain_event import GenericDomainEvent
from uuid import uuid4
from datetime import datetime


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def event_driven_lifespan() -> AsyncGenerator[None, None]:
    """事件驱动架构生命周期管理
    
    用于 FastAPI 或其他异步应用的生命周期管理
    """
    try:
        # 启动时初始化
        logger.info("Initializing event-driven architecture...")
        coordinator = await get_coordinator()
        
        # 检查协调器状态
        status = await coordinator.get_coordinator_status()
        logger.info(f"Event coordinator status: {status}")
        
        yield
        
    finally:
        # 关闭时清理
        logger.info("Shutting down event-driven architecture...")
        await shutdown_coordinator()
        logger.info("Event-driven architecture shut down successfully")


async def example_event_publishing():
    """事件发布示例"""
    logger.info("Starting event publishing example...")
    
    # 获取协调器
    coordinator = await get_coordinator()
    
    # 示例1: 发布用户注册事件
    user_registered_event = GenericDomainEvent(
        aggregate_id=uuid4(),
        event_type="UserRegistered",
        event_data={
            "user_id": str(uuid4()),
            "email": "user@example.com",
            "username": "newuser",
            "registration_source": "web",
            "user_agent": "Mozilla/5.0...",
            "ip_address": "192.168.1.1"
        },
        occurred_at=datetime.utcnow()
    )
    
    await publish_event(user_registered_event)
    logger.info("Published UserRegistered event")
    
    # 示例2: 发布订阅激活事件
    subscription_activated_event = GenericDomainEvent(
        aggregate_id=uuid4(),
        event_type="SubscriptionActivated",
        event_data={
            "subscription_id": str(uuid4()),
            "user_id": str(uuid4()),
            "plan_type": "premium",
            "user_email": "user@example.com",
            "activation_date": datetime.utcnow().isoformat(),
            "payment_method": "credit_card"
        },
        occurred_at=datetime.utcnow()
    )
    
    await publish_event(subscription_activated_event)
    logger.info("Published SubscriptionActivated event")
    
    # 示例3: 发布工作流执行开始事件
    workflow_started_event = GenericDomainEvent(
        aggregate_id=uuid4(),
        event_type="WorkflowExecutionStarted",
        event_data={
            "execution_id": str(uuid4()),
            "workflow_id": str(uuid4()),
            "workflow_name": "Data Processing Pipeline",
            "user_id": str(uuid4()),
            "workflow_type": "data_processing",
            "estimated_resources": {
                "cpu": "2 cores",
                "memory": "4GB",
                "estimated_duration": "30 minutes"
            },
            "notification_settings": {
                "notify_on_start": True,
                "notify_on_completion": True,
                "notify_on_failure": True
            }
        },
        occurred_at=datetime.utcnow()
    )
    
    await publish_event(workflow_started_event)
    logger.info("Published WorkflowExecutionStarted event")
    
    # 示例4: 发布内容发布事件
    content_published_event = GenericDomainEvent(
        aggregate_id=uuid4(),
        event_type="ContentPublished",
        event_data={
            "content_id": str(uuid4()),
            "user_id": str(uuid4()),
            "title": "My New Article",
            "content_type": "article",
            "content_size": 1024,
            "tags": ["technology", "programming", "python"],
            "category": "tech",
            "language": "en",
            "searchable": True,
            "user_trust_level": "new",
            "notification_settings": {
                "notify_on_publish": True
            }
        },
        occurred_at=datetime.utcnow()
    )
    
    await publish_event(content_published_event)
    logger.info("Published ContentPublished event")
    
    # 等待一段时间让事件处理完成
    await asyncio.sleep(2)
    
    # 查看协调器状态
    status = await coordinator.get_coordinator_status()
    logger.info(f"Final coordinator status: {status}")


async def example_event_history():
    """事件历史查询示例"""
    logger.info("Starting event history example...")
    
    coordinator = await get_coordinator()
    
    # 获取最近的事件历史
    recent_events = await coordinator.get_event_history(limit=10)
    logger.info(f"Found {len(recent_events)} recent events")
    
    for event in recent_events:
        logger.info(f"Event: {event.event_type} at {event.occurred_at}")
    
    # 获取特定类型的事件
    user_events = await coordinator.get_event_history(
        event_type="UserRegistered",
        limit=5
    )
    logger.info(f"Found {len(user_events)} UserRegistered events")


async def main():
    """主函数示例"""
    async with event_driven_lifespan():
        # 运行示例
        await example_event_publishing()
        await example_event_history()
        
        logger.info("All examples completed successfully")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())