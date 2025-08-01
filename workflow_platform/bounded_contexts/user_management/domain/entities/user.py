"""用户聚合根实体"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import Field

from shared_kernel.domain.base_entity import AggregateRoot
from shared_kernel.domain.value_objects import Email, Username, HashedPassword, UserStatus, UserRole
from ..events.user_events import UserRegisteredEvent, UserLoggedInEvent, UserStatusChangedEvent
from ..value_objects.user_profile import UserProfile


class User(AggregateRoot):
    """用户聚合根"""
    
    username: Username
    email: Email
    hashed_password: HashedPassword
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    role: UserRole = Field(default=UserRole.USER)
    last_login_at: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    profile: Optional[UserProfile] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # 如果是新创建的用户，记录注册事件
        if self.id and not hasattr(self, '_events_recorded'):
            self.record_event(UserRegisteredEvent(
                aggregate_id=str(self.id),
                user_id=self.id,
                username=str(self.username),
                email=str(self.email),
                role=self.role
            ))
            self._events_recorded = True
    
    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        hashed_password: str,
        role: UserRole = UserRole.USER,
        user_id: Optional[int] = None
    ) -> "User":
        """创建新用户"""
        import uuid
        # 为测试环境生成临时id，实际环境中由数据库分配
        temp_id = user_id or hash(str(uuid.uuid4())) % 1000000
        return cls(
            id=temp_id,
            username=Username(value=username),
            email=Email(value=email),
            hashed_password=HashedPassword(value=hashed_password),
            role=role,
            status=UserStatus.ACTIVE
        )
    
    def activate(self) -> None:
        """激活用户"""
        if self.status == UserStatus.ACTIVE:
            return  # 已经是激活状态
        
        old_status = self.status
        self.status = UserStatus.ACTIVE
        self.increment_version()
        
        self.record_event(UserStatusChangedEvent(
            aggregate_id=str(self.id),
            user_id=self.id,
            old_status=old_status,
            new_status=self.status
        ))
    
    def deactivate(self) -> None:
        """停用用户"""
        if self.status == UserStatus.INACTIVE:
            return
        
        old_status = self.status
        self.status = UserStatus.INACTIVE
        self.increment_version()
        
        self.record_event(UserStatusChangedEvent(
            aggregate_id=str(self.id),
            user_id=self.id,
            old_status=old_status,
            new_status=self.status
        ))
    
    def record_login(self, ip_address: Optional[str] = None) -> None:
        """记录用户登录"""
        self.last_login_at = datetime.now(timezone.utc)
        self.increment_version()
        
        self.record_event(UserLoggedInEvent(
            aggregate_id=str(self.id),
            user_id=self.id,
            ip_address=ip_address,
            login_time=self.last_login_at
        ))
    
    def update_password(self, new_hashed_password: str) -> None:
        """更新密码"""
        self.hashed_password = HashedPassword(value=new_hashed_password)
        self.password_changed_at = datetime.now(timezone.utc)
        self.increment_version()
    
    def update_profile(self, profile_data: Dict[str, Any]) -> None:
        """更新用户资料"""
        if self.profile:
            self.profile = self.profile.update(profile_data)
        else:
            self.profile = UserProfile(**profile_data)
        self.increment_version()
    
    def can_login(self) -> bool:
        """检查用户是否可以登录"""
        return self.status in [UserStatus.ACTIVE]
    
    def is_admin(self) -> bool:
        """检查用户是否为管理员"""
        return self.role == UserRole.ADMIN
    
    def is_active(self) -> bool:
        """检查用户是否处于活跃状态"""
        return self.status == UserStatus.ACTIVE
    
    class Config:
        from_attributes = True