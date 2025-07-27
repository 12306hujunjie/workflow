from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List
from uuid import UUID, uuid4
from dataclasses import dataclass


@dataclass
class DomainEvent(ABC):
    """领域事件基类"""
    
    def __init__(self, aggregate_id: UUID, event_data: Dict[str, Any]):
        self.id = uuid4()
        self.aggregate_id = aggregate_id
        self.event_data = event_data
        self.occurred_at = datetime.utcnow()
        self.event_version = 1
    
    @property
    @abstractmethod
    def event_type(self) -> str:
        """事件类型"""
        pass
    
    @property
    @abstractmethod
    def aggregate_type(self) -> str:
        """聚合根类型"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        return {
            'id': str(self.id),
            'aggregate_id': str(self.aggregate_id),
            'aggregate_type': self.aggregate_type,
            'event_type': self.event_type,
            'event_data': self.event_data,
            'event_version': self.event_version,
            'occurred_at': self.occurred_at.isoformat()
        }


class EventStore(ABC):
    """事件存储接口"""
    
    @abstractmethod
    async def save_event(self, event: DomainEvent) -> None:
        """保存事件"""
        pass
    
    @abstractmethod
    async def get_events(self, aggregate_id: UUID, from_version: int = 0, limit: int = 100) -> List[DomainEvent]:
        """获取聚合根的所有事件"""
        pass
    
    @abstractmethod
    async def get_events_by_type(self, event_type: str, limit: int = 100) -> List[DomainEvent]:
        """根据事件类型获取事件"""
        pass


class EventPublisher(ABC):
    """事件发布器接口"""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """发布事件"""
        pass
    
    @abstractmethod
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """批量发布事件"""
        pass


class EventHandler(ABC):
    """事件处理器基类"""
    
    @property
    @abstractmethod
    def handled_event_types(self) -> List[str]:
        """处理的事件类型列表"""
        pass
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """处理事件"""
        pass