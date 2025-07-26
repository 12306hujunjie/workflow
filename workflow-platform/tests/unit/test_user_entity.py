"""用户实体单元测试"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from bounded_contexts.user_management.domain.entities.user import User
from shared_kernel.domain.value_objects import (
    Username, Email, HashedPassword, UserStatus, UserRole
)
from bounded_contexts.user_management.domain.events.user_events import (
    UserRegisteredEvent, UserLoggedInEvent, UserStatusChangedEvent
)
from bounded_contexts.user_management.domain.value_objects.user_profile import UserProfile


class TestUserEntity:
    """用户实体测试"""
    
    def test_create_user(self):
        """测试创建用户"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        
        assert user.username.value == "testuser"
        assert user.email.value == "test@example.com"
        assert user.hashed_password.value == "hashed_password_123"
        # TODO: 等邮箱验证服务接入后，改回PENDING_VERIFICATION
        assert user.status == UserStatus.ACTIVE
        assert user.role == UserRole.USER
        assert user.id is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_user_activate(self):
        """测试激活用户"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        
        # 由于用户已经是ACTIVE状态，activate()不会改变状态
        original_version = user.version
        user.activate()
        
        assert user.status == UserStatus.ACTIVE
        assert user.version == original_version  # 版本号不变，因为已经是ACTIVE状态
        
        # 检查领域事件 - 由于用户已经是ACTIVE状态，不会产生新的状态变更事件
        events = user.get_domain_events()
        # 只会有初始的UserRegisteredEvent
        assert len(events) == 1
        assert any(isinstance(e, UserRegisteredEvent) for e in events)
    
    def test_user_activate_already_active(self):
        """测试重复激活用户"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        user.activate()
        initial_version = user.version
        
        # 尝试激活已激活的用户，应该不会抛出异常，也不会改变状态
        user.activate()
        assert user.status == UserStatus.ACTIVE
        assert user.version == initial_version  # 版本号不应该变化
    
    def test_user_deactivate(self):
        """测试停用用户"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        user.activate()
        
        user.deactivate()
        
        assert user.status == UserStatus.INACTIVE
        assert user.version == 2  # 创建(1) + 停用(2)，激活不会增加版本因为用户已经是ACTIVE
    
    def test_user_ban(self):
        """测试封禁用户"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        user.activate()
        
        user.ban()
        
        assert user.status == UserStatus.BANNED
        assert not user.can_login()
    
    def test_user_record_login(self):
        """测试记录用户登录"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        user.activate()
        
        ip_address = "192.168.1.1"
        user.record_login(ip_address)
        
        assert user.last_login_at is not None
        assert isinstance(user.last_login_at, datetime)
        
        # 检查领域事件
        events = user.get_domain_events()
        login_event = next(e for e in events if isinstance(e, UserLoggedInEvent))
        assert login_event.ip_address == ip_address
        assert login_event.login_time == user.last_login_at
    
    def test_user_update_password(self):
        """测试更新密码"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            hashed_password="old_hashed_password"
        )
        
        new_hashed_password = "new_hashed_password"
        user.update_password(new_hashed_password)
        
        assert user.hashed_password.value == new_hashed_password
        assert user.version == 2
    
    def test_user_update_profile(self):
        """测试更新用户资料"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        
        profile_data = {
            "display_name": "Test User",
            "bio": "Test bio",
            "avatar_url": "https://example.com/avatar.png"
        }
        
        user.update_profile(profile_data)
        
        assert user.profile is not None
        assert user.profile.display_name == profile_data["display_name"]
        assert user.profile.bio == profile_data["bio"]
        assert user.profile.avatar_url == profile_data["avatar_url"]
    
    def test_user_can_login(self):
        """测试用户登录权限检查"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        
        # TODO: 当前实现中用户创建时就是ACTIVE状态，等邮箱验证服务接入后再修改
        # 创建的用户当前默认就是ACTIVE状态，可以登录
        assert user.can_login()
        
        # 重复激活不会改变状态
        user.activate()
        assert user.can_login()
        
        # 停用后不能登录
        user.deactivate()
        assert not user.can_login()
        
        # 封禁后不能登录
        user.activate()
        user.ban()
        assert not user.can_login()
    
    def test_user_is_admin(self):
        """测试管理员权限检查"""
        # 普通用户
        user = User.create(
            username="normaluser",
            email="normal@example.com",
            hashed_password="hashed_password_123"
        )
        assert not user.is_admin()
        
        # 管理员用户
        admin = User.create(
            username="adminuser",
            email="admin@example.com",
            hashed_password="hashed_password_123",
            role=UserRole.ADMIN
        )
        assert admin.is_admin()
    
    def test_user_domain_events(self):
        """测试领域事件管理"""
        user = User.create(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        
        # 初始应该有事件
        events = user.get_domain_events()
        assert len(events) > 0
        
        # 清除事件
        user.clear_domain_events()
        assert len(user.get_domain_events()) == 0
        
        # 执行操作产生新事件 - 由于用户已经是ACTIVE状态，activate()不会产生事件
        # 改为使用deactivate()来测试事件生成
        user.deactivate()
        events = user.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], UserStatusChangedEvent)


class TestUserValueObjects:
    """用户值对象测试"""
    
    def test_username_validation(self):
        """测试用户名验证"""
        # 有效用户名
        username = Username(value="validuser123")
        assert username.value == "validuser123"
        
        # 无效用户名 - 太短
        with pytest.raises(ValueError):
            Username(value="ab")
        
        # 无效用户名 - 太长
        with pytest.raises(ValueError):
            Username(value="a" * 51)
        
        # 无效用户名 - 包含特殊字符
        with pytest.raises(ValueError, match="Username can only contain"):
            Username(value="user@123")
    
    def test_email_validation(self):
        """测试邮箱验证"""
        # 有效邮箱
        email = Email(value="test@example.com")
        assert email.value == "test@example.com"
        
        # 无效邮箱
        with pytest.raises(ValueError, match="Invalid email format"):
            Email(value="invalid-email")
        
        with pytest.raises(ValueError, match="Invalid email format"):
            Email(value="@example.com")
        
        with pytest.raises(ValueError, match="Invalid email format"):
            Email(value="test@")
    
    def test_user_profile(self):
        """测试用户资料值对象"""
        profile = UserProfile(
            display_name="Test User",
            bio="Test bio"
        )
        
        assert profile.display_name == "Test User"
        assert profile.bio == "Test bio"
        assert profile.timezone == "UTC"  # 默认值
        assert profile.language == "zh-CN"  # 默认值
        
        # 测试更新
        updated_profile = profile.update({
            "display_name": "Updated Name",
            "avatar_url": "https://example.com/avatar.png"
        })
        
        assert updated_profile.display_name == "Updated Name"
        assert updated_profile.avatar_url == "https://example.com/avatar.png"
        assert updated_profile.bio == "Test bio"  # 保持不变
        
        # 原profile不变（不可变）
        assert profile.display_name == "Test User"