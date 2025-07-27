"""共享内核数据库模型"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from .async_session import Base


class DomainEventModel(Base):
    """领域事件数据库模型
    
    用于持久化存储领域事件，支持事件溯源和跨模块事件处理
    """
    __tablename__ = "domain_events"
    
    # 主键：事件唯一标识
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 聚合根标识：事件所属的聚合根ID
    aggregate_id = Column(String(255), nullable=False, index=True)
    
    # 聚合根类型：事件所属的聚合根类型
    aggregate_type = Column(String(100), nullable=False, index=True)
    
    # 事件类型：具体的事件类型名称
    event_type = Column(String(255), nullable=False, index=True)
    
    # 事件版本：用于事件模式演进
    event_version = Column(Integer, nullable=False, default=1)
    
    # 事件数据：JSON格式存储事件的具体数据
    event_data = Column(JSONB, nullable=False)
    
    # 事件元数据：存储额外的元信息（如用户ID、IP地址等）
    event_metadata = Column(JSONB, nullable=True)
    
    # 创建时间：事件发生的时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # 序列号：同一聚合根内事件的顺序号
    sequence_number = Column(Integer, nullable=False)
    
    # 处理状态：标记事件是否已被处理
    is_processed = Column(Boolean, nullable=False, default=False, index=True)
    
    # 处理时间：事件被处理的时间
    processed_at = Column(DateTime, nullable=True)
    
    # 错误信息：处理失败时的错误信息
    error_message = Column(Text, nullable=True)
    
    # 重试次数：事件处理失败的重试次数
    retry_count = Column(Integer, nullable=False, default=0)
    
    # 索引定义
    __table_args__ = (
        # 复合索引：按聚合根和序列号查询
        Index('idx_aggregate_sequence', 'aggregate_id', 'sequence_number'),
        # 复合索引：按事件类型和创建时间查询
        Index('idx_event_type_created', 'event_type', 'created_at'),
        # 复合索引：按处理状态和创建时间查询（用于事件处理队列）
        Index('idx_processed_created', 'is_processed', 'created_at'),
        # 复合索引：按聚合根类型和创建时间查询
        Index('idx_aggregate_type_created', 'aggregate_type', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<DomainEventModel("
            f"id={self.id}, "
            f"aggregate_id='{self.aggregate_id}', "
            f"event_type='{self.event_type}', "
            f"created_at={self.created_at}"
            f")>"
        )
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'id': str(self.id),
            'aggregate_id': self.aggregate_id,
            'aggregate_type': self.aggregate_type,
            'event_type': self.event_type,
            'event_version': self.event_version,
            'event_data': self.event_data,
            'event_metadata': self.event_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sequence_number': self.sequence_number,
            'is_processed': self.is_processed,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count
        }