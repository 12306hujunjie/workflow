"""基础实体类和聚合根"""

import uuid
from abc import ABC
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    """领域事件基类"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    aggregate_id: str
    aggregate_type: str
    event_type: str
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
    
    class Config:
        frozen = True


class BaseEntity(BaseModel, ABC):
    """基础实体类"""
    id: Optional[int] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True
        validate_assignment = True


class AggregateRoot(BaseEntity, ABC):
    """聚合根基类"""
    version: int = Field(default=1)
    domain_events: List[DomainEvent] = Field(default_factory=list, exclude=True)
    
    def record_event(self, event: DomainEvent) -> None:
        """记录领域事件"""
        self.domain_events.append(event)
    
    def get_domain_events(self) -> List[DomainEvent]:
        """获取领域事件"""
        return self.domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """清空领域事件"""
        self.domain_events.clear()
    
    def increment_version(self) -> None:
        """增加版本号"""
        self.version += 1
        self.updated_at = datetime.utcnow()