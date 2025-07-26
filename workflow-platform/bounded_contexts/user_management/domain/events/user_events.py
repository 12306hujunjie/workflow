"""用户领域事件"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import Field

from shared_kernel.domain.base_entity import DomainEvent
from shared_kernel.domain.value_objects import UserStatus, UserRole


class UserRegisteredEvent(DomainEvent):
    """用户注册事件"""
    
    aggregate_type: Literal["User"] = "User"
    event_type: Literal["UserRegistered"] = "UserRegistered"
    
    user_id: Optional[int]
    username: str
    email: str
    role: UserRole


class UserLoggedInEvent(DomainEvent):
    """用户登录事件"""
    
    aggregate_type: Literal["User"] = "User"
    event_type: Literal["UserLoggedIn"] = "UserLoggedIn"
    
    user_id: int
    ip_address: Optional[str]
    login_time: datetime


class UserStatusChangedEvent(DomainEvent):
    """用户状态变更事件"""
    
    aggregate_type: Literal["User"] = "User"
    event_type: Literal["UserStatusChanged"] = "UserStatusChanged"
    
    user_id: int
    old_status: UserStatus
    new_status: UserStatus


# 注意：UserPasswordChangedEvent 和 UserProfileUpdatedEvent 已被移除
# 因为它们在代码中未被实际使用，且相关功能通过其他事件处理