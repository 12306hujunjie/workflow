"""事件驱动协调器

事件驱动架构的主要协调器，负责：
1. 初始化事件总线和相关组件
2. 注册跨模块事件处理器
3. 提供统一的事件发布接口
4. 管理事件处理器的生命周期
5. 提供事件监控和诊断功能
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Type
from uuid import UUID
from datetime import datetime

from shared_kernel.domain.events.domain_event import DomainEvent, EventHandler
from shared_kernel.domain.events.event_store import EventStore, SqlEventStore, SqlEventStoreWithSessionFactory
from shared_kernel.infrastructure.event_publisher import EventPublisher, EventPublisherFactory
from shared_kernel.infrastructure.database.async_session import db_config

from .event_bus import EventBus, EventBusFactory
from .event_handlers.user_event_handlers import (
    UserRegistrationEventHandler,
    UserStatusChangeEventHandler,
    UserLoginEventHandler
)
from .event_handlers.subscription_event_handlers import (
    SubscriptionActivationEventHandler,
    SubscriptionExpirationEventHandler
)
from .event_handlers.workflow_event_handlers import (
    WorkflowExecutionStartedEventHandler,
    WorkflowExecutionCompletedEventHandler,
    WorkflowExecutionFailedEventHandler
)
from .event_handlers.content_event_handlers import (
    ContentPublishedEventHandler,
    ContentModerationCompletedEventHandler,
    ContentDeletedEventHandler
)


logger = logging.getLogger(__name__)


class EventDrivenCoordinator:
    """事件驱动协调器
    
    负责管理整个事件驱动架构的核心组件
    """
    
    def __init__(
        self,
        event_store: Optional[EventStore] = None,
        event_publisher: Optional[EventPublisher] = None,
        event_bus: Optional[EventBus] = None
    ):
        self.event_store = event_store
        self.event_publisher = event_publisher
        self.event_bus = event_bus
        self._handlers_registry: Dict[str, List[EventHandler]] = {}
        self._is_initialized = False
        self._background_tasks: List[asyncio.Task] = []
    
    @property
    def is_initialized(self) -> bool:
        """检查协调器是否已初始化"""
        return self._is_initialized
    
    async def initialize(self) -> None:
        """初始化协调器"""
        if self._is_initialized:
            logger.warning("EventDrivenCoordinator is already initialized")
            return
        
        try:
            logger.info("Initializing EventDrivenCoordinator")
            
            # 1. 初始化核心组件
            await self._initialize_core_components()
            
            # 2. 注册事件处理器
            await self._register_event_handlers()
            
            # 3. 启动后台任务
            await self._start_background_tasks()
            
            self._is_initialized = True
            logger.info("EventDrivenCoordinator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize EventDrivenCoordinator: {str(e)}")
            raise
    
    async def shutdown(self) -> None:
        """关闭协调器"""
        if not self._is_initialized:
            return
        
        try:
            logger.info("Shutting down EventDrivenCoordinator")
            
            # 1. 停止后台任务
            await self._stop_background_tasks()
            
            # 2. 关闭事件发布器
            if self.event_publisher:
                await self.event_publisher.close()
            
            # 3. 关闭数据库连接
            if hasattr(self.event_store, 'db_config') and self.event_store.db_config:
                await self.event_store.db_config.close()
            
            # 4. 清理资源
            self._handlers_registry.clear()
            
            self._is_initialized = False
            logger.info("EventDrivenCoordinator shut down successfully")
            
        except Exception as e:
            logger.error(f"Failed to shutdown EventDrivenCoordinator: {str(e)}")
            raise
    
    async def publish_event(self, event: DomainEvent) -> None:
        """发布事件"""
        if not self._is_initialized:
            raise RuntimeError("EventDrivenCoordinator is not initialized")
        
        try:
            await self.event_bus.publish(event)
            logger.debug(f"Published event: {event.event_type}")
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {str(e)}")
            raise
    
    async def publish_events(self, events: List[DomainEvent]) -> None:
        """批量发布事件"""
        if not self._is_initialized:
            raise RuntimeError("EventDrivenCoordinator is not initialized")
        
        try:
            await self.event_bus.publish_batch(events)
            logger.debug(f"Published {len(events)} events")
            
        except Exception as e:
            logger.error(f"Failed to publish {len(events)} events: {str(e)}")
            raise
    
    async def register_handler(self, event_type: str, handler: EventHandler) -> None:
        """注册事件处理器"""
        try:
            self.event_bus.register_handler(event_type, handler)
            
            # 更新本地注册表
            if event_type not in self._handlers_registry:
                self._handlers_registry[event_type] = []
            self._handlers_registry[event_type].append(handler)
            
            logger.info(f"Registered handler {handler.__class__.__name__} for event type {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to register handler for event type {event_type}: {str(e)}")
            raise
    
    async def get_event_history(
        self,
        aggregate_id: Optional[UUID] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[DomainEvent]:
        """获取事件历史"""
        if not self._is_initialized:
            raise RuntimeError("EventDrivenCoordinator is not initialized")
        
        try:
            if event_type:
                return await self.event_bus.get_events_by_type(event_type, limit)
            elif aggregate_id:
                return await self.event_bus.get_event_history(aggregate_id, limit)
            else:
                # 如果都没有指定，返回最近的事件
                return await self.event_store.get_unprocessed_events(limit)
            
        except Exception as e:
            logger.error(f"Failed to get event history: {str(e)}")
            raise
    
    async def replay_events(
        self,
        aggregate_id: Optional[UUID] = None,
        event_type: Optional[str] = None,
        from_sequence: Optional[int] = None
    ) -> None:
        """重放事件"""
        if not self._is_initialized:
            raise RuntimeError("EventDrivenCoordinator is not initialized")
        
        try:
            if aggregate_id:
                from_version = from_sequence or 0
                await self.event_bus.replay_events(aggregate_id, from_version)
                logger.info(f"Replayed events for aggregate {aggregate_id}")
            else:
                raise ValueError("aggregate_id is required for event replay")
            
        except Exception as e:
            logger.error(f"Failed to replay events: {str(e)}")
            raise
    
    def get_registered_handlers(self) -> Dict[str, List[str]]:
        """获取已注册的处理器信息"""
        return {
            event_type: [handler.__class__.__name__ for handler in handlers]
            for event_type, handlers in self._handlers_registry.items()
        }
    
    async def get_coordinator_status(self) -> Dict[str, Any]:
        """获取协调器状态"""
        return {
            'initialized': self._is_initialized,
            'registered_handlers': self.get_registered_handlers(),
            'background_tasks_count': len(self._background_tasks),
            'event_store_type': self.event_store.__class__.__name__ if self.event_store else None,
            'event_publisher_type': self.event_publisher.__class__.__name__ if self.event_publisher else None,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _initialize_core_components(self) -> None:
        """初始化核心组件"""
        # 初始化事件存储
        if not self.event_store:
            # 创建一个专用的会话工厂，而不是直接使用会话
            self.event_store = SqlEventStoreWithSessionFactory(db_config)
        
        # 初始化事件发布器
        if not self.event_publisher:
            self.event_publisher = EventPublisherFactory.create_redis_publisher()
        
        # 初始化事件总线
        if not self.event_bus:
            self.event_bus = EventBusFactory.create_event_bus(
                event_store=self.event_store,
                event_publisher=self.event_publisher
            )
        
        logger.info("Core components initialized")
    
    async def _register_event_handlers(self) -> None:
        """注册所有跨模块事件处理器"""
        # 用户事件处理器
        await self.register_handler('UserRegistered', UserRegistrationEventHandler())
        await self.register_handler('UserStatusChanged', UserStatusChangeEventHandler())
        await self.register_handler('UserLoggedIn', UserLoginEventHandler())
        
        # 订阅事件处理器
        await self.register_handler('SubscriptionActivated', SubscriptionActivationEventHandler())
        await self.register_handler('SubscriptionExpired', SubscriptionExpirationEventHandler())
        
        # 工作流事件处理器
        await self.register_handler('WorkflowExecutionStarted', WorkflowExecutionStartedEventHandler())
        await self.register_handler('WorkflowExecutionCompleted', WorkflowExecutionCompletedEventHandler())
        await self.register_handler('WorkflowExecutionFailed', WorkflowExecutionFailedEventHandler())
        
        # 内容事件处理器
        await self.register_handler('ContentPublished', ContentPublishedEventHandler())
        await self.register_handler('ContentModerationCompleted', ContentModerationCompletedEventHandler())
        await self.register_handler('ContentDeleted', ContentDeletedEventHandler())
        
        logger.info("All event handlers registered")
    
    async def _start_background_tasks(self) -> None:
        """启动后台任务"""
        # 启动未处理事件处理任务
        unprocessed_task = asyncio.create_task(
            self._process_unprocessed_events_periodically()
        )
        self._background_tasks.append(unprocessed_task)
        
        # 启动事件监听任务
        listener_task = asyncio.create_task(
            self._listen_for_events()
        )
        self._background_tasks.append(listener_task)
        
        logger.info(f"Started {len(self._background_tasks)} background tasks")
    
    async def _stop_background_tasks(self) -> None:
        """停止后台任务"""
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self._background_tasks.clear()
        logger.info("All background tasks stopped")
    
    async def _process_unprocessed_events_periodically(self) -> None:
        """定期处理未处理的事件"""
        while True:
            try:
                await asyncio.sleep(30)  # 每30秒检查一次
                await self.event_bus.process_unprocessed_events()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic unprocessed events processing: {str(e)}")
                await asyncio.sleep(60)  # 出错时等待更长时间
    
    async def _listen_for_events(self) -> None:
        """监听事件发布"""
        try:
            await self.event_publisher.listen(self._handle_published_event)
            
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in event listener: {str(e)}")
    
    async def _handle_published_event(self, event_data: Dict[str, Any]) -> None:
        """处理发布的事件"""
        try:
            # 这里可以添加额外的事件处理逻辑
            # 比如监控、日志记录、指标收集等
            logger.debug(f"Received published event: {event_data.get('event_type')}")
            
        except Exception as e:
            logger.error(f"Error handling published event: {str(e)}")


# 全局协调器实例
_coordinator: Optional[EventDrivenCoordinator] = None


async def get_coordinator() -> EventDrivenCoordinator:
    """获取全局协调器实例"""
    global _coordinator
    
    if _coordinator is None:
        _coordinator = EventDrivenCoordinator()
        await _coordinator.initialize()
    
    return _coordinator


async def shutdown_coordinator() -> None:
    """关闭全局协调器实例"""
    global _coordinator
    
    if _coordinator is not None:
        await _coordinator.shutdown()
        _coordinator = None


# 便捷函数
async def publish_event(event: DomainEvent) -> None:
    """发布事件的便捷函数"""
    coordinator = await get_coordinator()
    await coordinator.publish_event(event)


async def publish_events(events: List[DomainEvent]) -> None:
    """批量发布事件的便捷函数"""
    coordinator = await get_coordinator()
    await coordinator.publish_events(events)


async def register_handler(event_type: str, handler: EventHandler) -> None:
    """注册事件处理器的便捷函数"""
    coordinator = await get_coordinator()
    await coordinator.register_handler(event_type, handler)