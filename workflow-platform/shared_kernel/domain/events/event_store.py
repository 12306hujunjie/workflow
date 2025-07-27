from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json

from .domain_event import DomainEvent, EventStore
from ...infrastructure.database.models import DomainEventModel
from ...infrastructure.database.async_session import DatabaseConfig


class SqlEventStore(EventStore):
    """基于SQL数据库的事件存储实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_event(self, event: DomainEvent) -> None:
        """保存事件到数据库"""
        # 获取下一个序列号
        sequence_number = await self._get_next_sequence_number(event.aggregate_id)
        
        event_model = DomainEventModel(
            id=event.id,
            aggregate_id=str(event.aggregate_id),
            aggregate_type=event.aggregate_type,
            event_type=event.event_type,
            event_data=event.event_data,
            event_version=event.event_version,
            created_at=event.occurred_at,
            sequence_number=sequence_number,
            event_metadata=getattr(event, 'metadata', None)
        )
        
        self.session.add(event_model)
        # 不在这里提交，由外部会话管理器控制
    
    async def get_events(self, aggregate_id: UUID, from_version: int = 0, limit: int = 100) -> List[DomainEvent]:
        """获取聚合根的所有事件"""
        stmt = select(DomainEventModel).where(
            and_(
                DomainEventModel.aggregate_id == str(aggregate_id),
                DomainEventModel.event_version >= from_version
            )
        ).order_by(DomainEventModel.sequence_number).limit(limit)
        
        result = await self.session.execute(stmt)
        event_models = result.scalars().all()
        
        return [self._model_to_event(model) for model in event_models]
    
    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[DomainEvent]:
        """根据事件类型获取事件"""
        stmt = select(DomainEventModel).where(
            DomainEventModel.event_type == event_type
        ).order_by(DomainEventModel.created_at.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        event_models = result.scalars().all()
        
        return [self._model_to_event(model) for model in event_models]
    
    async def get_unprocessed_events(self, limit: int = 100) -> List[DomainEvent]:
        """获取未处理的事件"""
        stmt = select(DomainEventModel).where(
            DomainEventModel.is_processed == False
        ).order_by(DomainEventModel.created_at).limit(limit)
        
        result = await self.session.execute(stmt)
        event_models = result.scalars().all()
        
        return [self._model_to_event(model) for model in event_models]
    
    async def mark_event_processed(self, event_id: UUID) -> None:
        """标记事件为已处理"""
        stmt = select(DomainEventModel).where(DomainEventModel.id == event_id)
        result = await self.session.execute(stmt)
        event_model = result.scalar_one_or_none()
        
        if event_model:
            event_model.is_processed = True
            event_model.processed_at = datetime.utcnow()
            # 不在这里提交，由外部会话管理器控制
    
    async def mark_event_failed(self, event_id: UUID, error_message: str) -> None:
        """标记事件处理失败"""
        stmt = select(DomainEventModel).where(DomainEventModel.id == event_id)
        result = await self.session.execute(stmt)
        event_model = result.scalar_one_or_none()
        
        if event_model:
            event_model.retry_count += 1
            event_model.error_message = error_message
            # 不在这里提交，由外部会话管理器控制
    
    async def _get_next_sequence_number(self, aggregate_id: UUID) -> int:
        """获取聚合根的下一个序列号"""
        stmt = select(func.max(DomainEventModel.sequence_number)).where(
            DomainEventModel.aggregate_id == str(aggregate_id)
        )
        result = await self.session.execute(stmt)
        max_sequence = result.scalar()
        return (max_sequence or 0) + 1
    
    async def get_events_by_aggregate_id(self, aggregate_id: UUID, limit: int = 100) -> List[DomainEvent]:
        """根据聚合ID获取事件"""
        return await self.get_events(aggregate_id, from_version=0, limit=limit)
    
    def _model_to_event(self, model: DomainEventModel) -> DomainEvent:
        """将数据库模型转换为领域事件"""
        # 这里需要根据事件类型创建具体的事件实例
        # 为了简化，我们创建一个通用的事件类
        return GenericDomainEvent(
            event_id=model.id,
            aggregate_id=UUID(model.aggregate_id),
            aggregate_type=model.aggregate_type,
            event_type=model.event_type,
            event_data=model.event_data,
            event_version=model.event_version,
            occurred_at=model.created_at,
            metadata=model.event_metadata
        )


class GenericDomainEvent(DomainEvent):
    """通用领域事件，用于从存储中重建事件"""
    
    def __init__(self, event_id: UUID, aggregate_id: UUID, aggregate_type: str, 
                 event_type: str, event_data: dict, event_version: int, 
                 occurred_at: datetime, metadata: Optional[dict] = None):
        self.id = event_id
        self.aggregate_id = aggregate_id
        self._aggregate_type = aggregate_type
        self._event_type = event_type
        self.event_data = event_data
        self.event_version = event_version
        self.occurred_at = occurred_at
        self.metadata = metadata or {}
    
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
    
    async def get_events(self, aggregate_id: UUID, from_version: int = 0, limit: int = 100) -> List[DomainEvent]:
        events = [
            event for event in self._events 
            if event.aggregate_id == aggregate_id and event.event_version >= from_version
        ]
        return events[-limit:] if len(events) > limit else events
    
    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[DomainEvent]:
        events = [event for event in self._events if event.event_type == event_type]
        return events[-limit:] if len(events) > limit else events
    
    async def get_unprocessed_events(self, limit: int = 100) -> List[DomainEvent]:
        """获取未处理的事件（内存版本简化实现）"""
        return self._events[-limit:] if len(self._events) > limit else self._events
    
    async def mark_event_processed(self, event_id: UUID) -> None:
        """标记事件为已处理（内存版本简化实现）"""
        # 内存版本不需要实际标记，因为我们不跟踪处理状态
        pass
    
    async def mark_event_failed(self, event_id: UUID, error_message: str) -> None:
        """标记事件处理失败（内存版本简化实现）"""
        # 内存版本不需要实际标记，因为我们不跟踪处理状态
        pass
    
    async def get_events_by_aggregate_id(self, aggregate_id: UUID, limit: int = 100) -> List[DomainEvent]:
        """根据聚合ID获取事件"""
        events = [event for event in self._events if event.aggregate_id == aggregate_id]
        return events[-limit:] if len(events) > limit else events


class SqlEventStoreWithSessionFactory(EventStore):
    """使用会话工厂的SQL事件存储实现"""
    
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
    
    async def save_event(self, event: DomainEvent) -> None:
        """保存事件到数据库"""
        async with self.db_config.session_scope() as session:
            try:
                store = SqlEventStore(session)
                await store.save_event(event)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def get_events(self, aggregate_id: UUID, from_version: int = 0, limit: int = 100) -> List[DomainEvent]:
        """获取聚合根的所有事件"""
        async with self.db_config.session_scope() as session:
            store = SqlEventStore(session)
            return await store.get_events(aggregate_id, from_version, limit)
    
    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[DomainEvent]:
        """根据事件类型获取事件"""
        async with self.db_config.session_scope() as session:
            store = SqlEventStore(session)
            return await store.get_events_by_type(event_type, limit)
    
    async def get_unprocessed_events(self, limit: int = 100) -> List[DomainEvent]:
        """获取未处理的事件"""
        async with self.db_config.session_scope() as session:
            store = SqlEventStore(session)
            return await store.get_unprocessed_events(limit)
    
    async def mark_event_processed(self, event_id: UUID) -> None:
        """标记事件为已处理"""
        async with self.db_config.session_scope() as session:
            try:
                store = SqlEventStore(session)
                await store.mark_event_processed(event_id)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def mark_event_failed(self, event_id: UUID, error_message: str) -> None:
        """标记事件处理失败"""
        async with self.db_config.session_scope() as session:
            try:
                store = SqlEventStore(session)
                await store.mark_event_failed(event_id, error_message)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def get_events_by_aggregate_id(self, aggregate_id: UUID, limit: int = 100) -> List[DomainEvent]:
        """根据聚合ID获取事件"""
        async with self.db_config.session_scope() as session:
            store = SqlEventStore(session)
            return await store.get_events_by_aggregate_id(aggregate_id, limit)
    
    def clear(self):
        """清空所有事件，用于测试"""
        self._events.clear()