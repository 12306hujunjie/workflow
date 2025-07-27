"""事件总线 - 事件驱动架构的核心协调器"""

from typing import Dict, List, Callable, Optional, Any
from abc import ABC, abstractmethod
import asyncio
import logging
from datetime import datetime
from uuid import UUID

from shared_kernel.domain.events.domain_event import DomainEvent, EventHandler
from shared_kernel.domain.events.event_store import EventStore
from shared_kernel.infrastructure.event_publisher import EventPublisher


logger = logging.getLogger(__name__)


class EventBus:
    """事件总线
    
    负责协调事件的存储、发布和处理，是事件驱动架构的核心组件
    """
    
    def __init__(self, event_store: EventStore, event_publisher: EventPublisher):
        self.event_store = event_store
        self.event_publisher = event_publisher
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._middleware: List[Callable] = []
        self._is_processing = False
    
    async def publish(self, event: DomainEvent) -> None:
        """发布单个事件"""
        try:
            # 1. 应用中间件
            processed_event = await self._apply_middleware(event)
            
            # 2. 存储事件
            await self.event_store.save_event(processed_event)
            
            # 3. 发布事件到消息队列
            await self.event_publisher.publish(processed_event)
            
            # 4. 同步处理本地事件处理器
            await self._handle_event_locally(processed_event)
            
            logger.info(f"Successfully published event {event.event_type} for aggregate {event.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {str(e)}")
            # 标记事件处理失败
            if hasattr(self.event_store, 'mark_event_failed'):
                await self.event_store.mark_event_failed(event.id, str(e))
            raise
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """批量发布事件"""
        if not events:
            return
        
        try:
            # 1. 应用中间件到所有事件
            processed_events = []
            for event in events:
                processed_event = await self._apply_middleware(event)
                processed_events.append(processed_event)
            
            # 2. 批量存储事件
            for event in processed_events:
                await self.event_store.save_event(event)
            
            # 3. 批量发布事件
            await self.event_publisher.publish_batch(processed_events)
            
            # 4. 同步处理本地事件处理器
            for event in processed_events:
                await self._handle_event_locally(event)
            
            logger.info(f"Successfully published {len(events)} events in batch")
            
        except Exception as e:
            logger.error(f"Failed to publish batch events: {str(e)}")
            raise
    
    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        """注册事件处理器"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        logger.info(f"Registered handler {handler.__class__.__name__} for event type {event_type}")
    
    def register_handlers(self, handlers: Dict[str, List[EventHandler]]) -> None:
        """批量注册事件处理器"""
        for event_type, handler_list in handlers.items():
            for handler in handler_list:
                self.register_handler(event_type, handler)
    
    def add_middleware(self, middleware: Callable) -> None:
        """添加事件处理中间件"""
        self._middleware.append(middleware)
        logger.info(f"Added middleware {middleware.__name__}")
    
    async def start_processing(self) -> None:
        """开始处理未处理的事件"""
        if self._is_processing:
            logger.warning("Event processing is already running")
            return
        
        self._is_processing = True
        logger.info("Started event processing")
        
        try:
            while self._is_processing:
                await self._process_unprocessed_events()
                await asyncio.sleep(1)  # 避免过于频繁的轮询
        except Exception as e:
            logger.error(f"Error in event processing: {str(e)}")
        finally:
            self._is_processing = False
    
    def stop_processing(self) -> None:
        """停止事件处理"""
        self._is_processing = False
        logger.info("Stopped event processing")
    
    async def replay_events(self, aggregate_id: UUID, from_version: int = 0) -> None:
        """重放聚合根的事件"""
        try:
            events = await self.event_store.get_events(aggregate_id, from_version, limit=1000)
            
            for event in events:
                await self._handle_event_locally(event)
            
            logger.info(f"Replayed {len(events)} events for aggregate {aggregate_id}")
            
        except Exception as e:
            logger.error(f"Failed to replay events for aggregate {aggregate_id}: {str(e)}")
            raise
    
    async def get_event_history(self, aggregate_id: UUID, limit: int = 100) -> List[DomainEvent]:
        """获取聚合根的事件历史"""
        return await self.event_store.get_events(aggregate_id, limit)
    
    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[DomainEvent]:
        """根据事件类型获取事件"""
        return await self.event_store.get_events_by_type(event_type, limit)
    
    async def process_unprocessed_events(self) -> int:
        """处理未处理的事件（公共接口）"""
        return await self._process_unprocessed_events()
    

    
    async def _apply_middleware(self, event: DomainEvent) -> DomainEvent:
        """应用中间件处理事件"""
        processed_event = event
        
        for middleware in self._middleware:
            try:
                if asyncio.iscoroutinefunction(middleware):
                    processed_event = await middleware(processed_event)
                else:
                    processed_event = middleware(processed_event)
            except Exception as e:
                logger.error(f"Error in middleware {middleware.__name__}: {str(e)}")
                raise
        
        return processed_event
    
    async def _handle_event_locally(self, event: DomainEvent) -> None:
        """处理本地事件处理器"""
        handlers = self._handlers.get(event.event_type, [])
        
        if not handlers:
            logger.debug(f"No local handlers found for event type {event.event_type}")
            return
        
        # 并行执行所有处理器
        tasks = []
        for handler in handlers:
            task = asyncio.create_task(self._safe_handle(handler, event))
            tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 检查是否有处理失败
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Handler {handlers[i].__class__.__name__} failed: {str(result)}")
    
    async def _safe_handle(self, handler: EventHandler, event: DomainEvent) -> None:
        """安全地执行事件处理器"""
        try:
            await handler.handle(event)
            logger.debug(f"Handler {handler.__class__.__name__} processed event {event.event_type}")
        except Exception as e:
            logger.error(f"Error in handler {handler.__class__.__name__}: {str(e)}")
            raise
    
    async def _process_unprocessed_events(self) -> int:
        """处理未处理的事件"""
        processed_count = 0
        try:
            unprocessed_events = await self.event_store.get_unprocessed_events(limit=50)
            
            for event in unprocessed_events:
                try:
                    # 处理事件
                    await self._handle_event_locally(event)
                    
                    # 标记为已处理
                    await self.event_store.mark_event_processed(event.id)
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process event {event.id}: {str(e)}")
                    
                    # 标记处理失败
                    if hasattr(self.event_store, 'mark_event_failed'):
                        await self.event_store.mark_event_failed(event.id, str(e))
        
        except Exception as e:
            logger.error(f"Error processing unprocessed events: {str(e)}")
        
        return processed_count


class EventBusMiddleware:
    """事件总线中间件基类"""
    
    @staticmethod
    def logging_middleware(event: DomainEvent) -> DomainEvent:
        """日志中间件"""
        logger.info(f"Processing event {event.event_type} for aggregate {event.aggregate_id}")
        return event
    
    @staticmethod
    def metadata_enrichment_middleware(event: DomainEvent) -> DomainEvent:
        """元数据丰富中间件"""
        if not hasattr(event, 'metadata'):
            event.metadata = {}
        
        event.metadata.update({
            'processed_at': datetime.utcnow().isoformat(),
            'processor': 'event_bus'
        })
        
        return event
    
    @staticmethod
    def validation_middleware(event: DomainEvent) -> DomainEvent:
        """验证中间件"""
        if not event.id:
            raise ValueError("Event ID is required")
        
        if not event.aggregate_id:
            raise ValueError("Aggregate ID is required")
        
        if not event.event_type:
            raise ValueError("Event type is required")
        
        return event


class EventBusFactory:
    """事件总线工厂"""
    
    @staticmethod
    def create_event_bus(event_store: EventStore, event_publisher: EventPublisher) -> EventBus:
        """创建事件总线"""
        event_bus = EventBus(event_store, event_publisher)
        
        # 添加默认中间件
        event_bus.add_middleware(EventBusMiddleware.validation_middleware)
        event_bus.add_middleware(EventBusMiddleware.metadata_enrichment_middleware)
        event_bus.add_middleware(EventBusMiddleware.logging_middleware)
        
        return event_bus