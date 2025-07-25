"""用户领域事件"""

from datetime import datetime
from typing import Optional
from pydantic import Field

from shared_kernel.domain.base_entity import DomainEvent
from shared_kernel.domain.value_objects import UserStatus, UserRole


class UserRegisteredEvent(DomainEvent):
    """用户注册事件"""
    
    aggregate_type: str = Field(default="User", const=True)
    event_type: str = Field(default="UserRegistered", const=True)
    
    user_id: Optional[int]
    username: str
    email: str
    role: UserRole


class UserLoggedInEvent(DomainEvent):
    """用户登录事件"""
    
    aggregate_type: str = Field(default="User", const=True)
    event_type: str = Field(default="UserLoggedIn", const=True)
    
    user_id: int
    ip_address: Optional[str]
    login_time: datetime


class UserStatusChangedEvent(DomainEvent):
    """用户状态变更事件"""
    
    aggregate_type: str = Field(default="User", const=True)
    event_type: str = Field(default="UserStatusChanged", const=True)
    
    user_id: int
    old_status: UserStatus
    new_status: UserStatus


class UserPasswordChangedEvent(DomainEvent):
    """用户密码变更事件"""
    
    aggregate_type: str = Field(default="User", const=True)
    event_type: str = Field(default="UserPasswordChanged", const=True)
    
    user_id: int


class UserProfileUpdatedEvent(DomainEvent):
    """用户资料更新事件"""
    
    aggregate_type: str = Field(default="User", const=True)
    event_type: str = Field(default="UserProfileUpdated", const=True)
    
    user_id: int
    updated_fields: list[str]