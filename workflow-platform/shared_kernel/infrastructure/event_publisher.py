"""事件发布器实现"""

from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import json
import asyncio
import logging
from datetime import datetime
from uuid import UUID

import redis.asyncio as redis
from redis.asyncio import Redis

from ..domain.events.domain_event import DomainEvent, EventPublisher


logger = logging.getLogger(__name__)


class RedisEventPublisher(EventPublisher):
    """基于 Redis 的事件发布器
    
    使用 Redis Pub/Sub 机制实现事件的异步发布和订阅
    """
    
    def __init__(self, redis_client: Redis, channel_prefix: str = "domain_events"):
        self.redis_client = redis_client
        self.channel_prefix = channel_prefix
        self._subscribers: Dict[str, List[callable]] = {}
        self._pubsub = None
    
    async def publish(self, event: DomainEvent) -> None:
        """发布事件到 Redis"""
        try:
            # 构建事件消息
            event_message = {
                'id': str(event.id),
                'aggregate_id': str(event.aggregate_id),
                'aggregate_type': event.aggregate_type,
                'event_type': event.event_type,
                'event_data': event.event_data,
                'event_version': event.event_version,
                'occurred_at': event.occurred_at.isoformat(),
                'metadata': getattr(event, 'metadata', {})
            }
            
            # 发布到通用事件频道
            general_channel = f"{self.channel_prefix}:all"
            await self.redis_client.publish(general_channel, json.dumps(event_message))
            
            # 发布到特定事件类型频道
            type_channel = f"{self.channel_prefix}:type:{event.event_type}"
            await self.redis_client.publish(type_channel, json.dumps(event_message))
            
            # 发布到特定聚合类型频道
            aggregate_channel = f"{self.channel_prefix}:aggregate:{event.aggregate_type}"
            await self.redis_client.publish(aggregate_channel, json.dumps(event_message))
            
            logger.info(f"Published event {event.event_type} for aggregate {event.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {str(e)}")
            raise
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """批量发布事件"""
        if not events:
            return
        
        # 使用 Redis pipeline 提高性能
        pipe = self.redis_client.pipeline()
        
        try:
            for event in events:
                event_message = {
                    'id': str(event.id),
                    'aggregate_id': str(event.aggregate_id),
                    'aggregate_type': event.aggregate_type,
                    'event_type': event.event_type,
                    'event_data': event.event_data,
                    'event_version': event.event_version,
                    'occurred_at': event.occurred_at.isoformat(),
                    'metadata': getattr(event, 'metadata', {})
                }
                
                message_json = json.dumps(event_message)
                
                # 添加到 pipeline
                pipe.publish(f"{self.channel_prefix}:all", message_json)
                pipe.publish(f"{self.channel_prefix}:type:{event.event_type}", message_json)
                pipe.publish(f"{self.channel_prefix}:aggregate:{event.aggregate_type}", message_json)
            
            # 执行批量发布
            await pipe.execute()
            
            logger.info(f"Published {len(events)} events in batch")
            
        except Exception as e:
            logger.error(f"Failed to publish batch events: {str(e)}")
            raise
    
    async def listen(self, event_type: str, handler: callable) -> None:
        """监听特定类型的事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        
        if self._pubsub is None:
            self._pubsub = self.redis_client.pubsub()
        
        channel = f"{self.channel_prefix}:type:{event_type}"
        await self._pubsub.subscribe(channel)
    
    async def close(self) -> None:
        """关闭事件发布器"""
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
            self._pubsub = None
        self._subscribers.clear()
    
    async def subscribe(self, event_type: str, handler: callable) -> None:
        """订阅特定类型的事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler for event type: {event_type}")
    
    async def subscribe_all(self, handler: callable) -> None:
        """订阅所有事件"""
        if 'all' not in self._subscribers:
            self._subscribers['all'] = []
        
        self._subscribers['all'].append(handler)
        logger.info("Subscribed handler for all events")
    
    async def start_listening(self) -> None:
        """开始监听事件"""
        pubsub = self.redis_client.pubsub()
        
        try:
            # 订阅所有事件频道
            await pubsub.subscribe(f"{self.channel_prefix}:all")
            
            # 订阅特定事件类型频道
            for event_type in self._subscribers.keys():
                if event_type != 'all':
                    await pubsub.subscribe(f"{self.channel_prefix}:type:{event_type}")
            
            logger.info("Started listening for events")
            
            # 处理消息
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    await self._handle_message(message)
                    
        except Exception as e:
            logger.error(f"Error in event listener: {str(e)}")
            raise
        finally:
            await pubsub.close()
    
    async def _handle_message(self, message: dict) -> None:
        """处理接收到的消息"""
        try:
            # 解析事件数据
            event_data = json.loads(message['data'])
            event_type = event_data['event_type']
            
            # 调用所有事件处理器
            handlers = self._subscribers.get('all', [])
            
            # 调用特定事件类型处理器
            handlers.extend(self._subscribers.get(event_type, []))
            
            # 异步执行所有处理器
            tasks = []
            for handler in handlers:
                task = asyncio.create_task(self._safe_handle(handler, event_data))
                tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
    
    async def _safe_handle(self, handler: callable, event_data: dict) -> None:
        """安全地执行事件处理器"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event_data)
            else:
                handler(event_data)
        except Exception as e:
            logger.error(f"Error in event handler: {str(e)}")


class InMemoryEventPublisher(EventPublisher):
    """内存事件发布器，用于测试"""
    
    def __init__(self):
        self._published_events: List[DomainEvent] = []
        self._subscribers: Dict[str, List[callable]] = {}
    
    async def publish(self, event: DomainEvent) -> None:
        """发布事件到内存"""
        self._published_events.append(event)
        
        # 通知订阅者
        handlers = self._subscribers.get('all', [])
        handlers.extend(self._subscribers.get(event.event_type, []))
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {str(e)}")
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """批量发布事件"""
        for event in events:
            await self.publish(event)
    
    async def subscribe(self, event_type: str, handler: callable) -> None:
        """订阅特定类型的事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
    
    async def subscribe_all(self, handler: callable) -> None:
        """订阅所有事件"""
        if 'all' not in self._subscribers:
            self._subscribers['all'] = []
        
        self._subscribers['all'].append(handler)
    
    def get_published_events(self) -> List[DomainEvent]:
        """获取已发布的事件（测试用）"""
        return self._published_events.copy()
    
    def clear(self) -> None:
        """清空事件（测试用）"""
        self._published_events.clear()
        self._subscribers.clear()
    
    async def close(self) -> None:
        """关闭发布器（测试用）"""
        self.clear()
    
    async def listen(self, handler: callable) -> None:
        """监听事件（测试用）"""
        await self.subscribe_all(handler)


class EventPublisherFactory:
    """事件发布器工厂"""
    
    @staticmethod
    def create_redis_publisher(redis_url: str = "redis://localhost:6379", 
                             channel_prefix: str = "domain_events") -> RedisEventPublisher:
        """创建 Redis 事件发布器"""
        redis_client = redis.from_url(redis_url, decode_responses=True)
        return RedisEventPublisher(redis_client, channel_prefix)
    
    @staticmethod
    def create_memory_publisher() -> InMemoryEventPublisher:
        """创建内存事件发布器"""
        return InMemoryEventPublisher()