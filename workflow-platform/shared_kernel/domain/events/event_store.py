from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json

from .domain_event import DomainEvent, EventStore
from ...infrastructure.database.models import DomainEventModel


class SqlEventStore(EventStore):
    """基于SQL数据库的事件存储实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_event(self, event: DomainEvent) -> None:
        """保存事件到数据库"""
        event_model = DomainEventModel(
            id=event.id,
            aggregate_id=event.aggregate_id,
            aggregate_type=event.aggregate_type,
            event_type=event.event_type,
            event_data=event.event_data,
            event_version=event.event_version,
            occurred_at=event.occurred_at
        )
        
        self.session.add(event_model)
        await self.session.commit()
    
    async def get_events(self, aggregate_id: UUID, from_version: int = 0) -> List[DomainEvent]:
        """获取聚合根的所有事件"""
        stmt = select(DomainEventModel).where(
            and_(
                DomainEventModel.aggregate_id == aggregate_id,
                DomainEventModel.event_version >= from_version
            )
        ).order_by(DomainEventModel.event_version)
        
        result = await self.session.execute(stmt)
        event_models = result.scalars().all()
        
        return [self._model_to_event(model) for model in event_models]
    
    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[DomainEvent]:
        """根据事件类型获取事件"""
        stmt = select(DomainEventModel).where(
            DomainEventModel.event_type == event_type
        ).order_by(DomainEventModel.occurred_at.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        event_models = result.scalars().all()
        
        return [self._model_to_event(model) for model in event_models]
    
    async def get_unprocessed_events(self, limit: int = 100) -> List[DomainEvent]:
        """获取未处理的事件"""
        stmt = select(DomainEventModel).where(
            DomainEventModel.processed_at.is_(None)
        ).order_by(DomainEventModel.occurred_at).limit(limit)
        
        result = await self.session.execute(stmt)
        event_models = result.scalars().all()
        
        return [self._model_to_event(model) for model in event_models]
    
    async def mark_event_processed(self, event_id: UUID) -> None:
        """标记事件为已处理"""
        stmt = select(DomainEventModel).where(DomainEventModel.id == event_id)
        result = await self.session.execute(stmt)
        event_model = result.scalar_one_or_none()
        
        if event_model:
            event_model.processed_at = datetime.utcnow()
            await self.session.commit()
    
    def _model_to_event(self, model: DomainEventModel) -> DomainEvent:
        """将数据库模型转换为领域事件"""
        # 这里需要根据事件类型创建具体的事件实例
        # 为了简化，我们创建一个通用的事件类
        return GenericDomainEvent(
            event_id=model.id,
            aggregate_id=model.aggregate_id,
            aggregate_type=model.aggregate_type,
            event_type=model.event_type,
            event_data=model.event_data,
            event_version=model.event_version,
            occurred_at=model.occurred_at
        )


class GenericDomainEvent(DomainEvent):
    """通用领域事件，用于从存储中重建事件"""
    
    def __init__(self, event_id: UUID, aggregate_id: UUID, aggregate_type: str, 
                 event_type: str, event_data: dict, event_version: int, occurred_at: datetime):
        self.id = event_id
        self.aggregate_id = aggregate_id
        self._aggregate_type = aggregate_type
        self._event_type = event_type
        self.event_data = event_data
        self.event_version = event_version
        self.occurred_at = occurred_at
    
    @property
    def event_type(self) -> str:
        return self._event_type
    
    @property
    def aggregate_type(self) -> str:
        return self._aggregate_type


class InMemoryEventStore(EventStore):
    """内存事件存储，用于测试"""
    
    def __init__(self):
        self._events: List[DomainEvent] = []
    
    async def save_event(self, event: DomainEvent) -> None:
        self._events.append(event)
    
    async def get_events(self, aggregate_id: UUID, from_version: int = 0) -> List[DomainEvent]:
        return [
            event for event in self._events 
            if event.aggregate_id == aggregate_id and event.event_version >= from_version
        ]
    
    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[DomainEvent]:
        events = [event for event in self._events if event.event_type == event_type]
        return events[-limit:] if len(events) > limit else events
    
    def clear(self):
        """清空所有事件，用于测试"""
        self._events.clear()