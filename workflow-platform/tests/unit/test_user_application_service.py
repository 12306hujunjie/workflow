"""用户应用服务单元测试"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta

from bounded_contexts.user_management.application.services.user_application_service import (
    UserApplicationService
)
from bounded_contexts.user_management.application.commands.user_commands import (
    RegisterUserCommand, LoginUserCommand, UpdateUserProfileCommand, ChangePasswordCommand
)
from bounded_contexts.user_management.domain.entities.user import User
from shared_kernel.domain.value_objects import (
    Username, Email, HashedPassword, UserStatus, UserRole
)
from bounded_contexts.user_management.domain.exceptions import (
    UserAlreadyExistsError, InvalidCredentialsError, UserNotFoundError
)


@pytest.mark.asyncio
class TestUserApplicationService:
    """用户应用服务测试"""
    
    async def test_register_user_success(self, mock_unit_of_work, password_service, jwt_service):
        """测试成功注册用户"""
        # 准备
        mock_unit_of_work.users.find_by_username.return_value = None
        mock_unit_of_work.users.find_by_email.return_value = None
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        command = RegisterUserCommand(
            username="newuser",
            email="new@example.com",
            password="Test@123456"
        )
        
        # 执行
        result = await service.register_user(command)
        
        # 验证
        assert result["username"] == "newuser"
        assert result["email"] == "new@example.com"
        assert result["status"] == UserStatus.PENDING_VERIFICATION.value
        assert "id" in result
        
        # 验证调用
        mock_unit_of_work.users.save.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()
    
    async def test_register_user_username_exists(self, mock_unit_of_work, password_service, jwt_service):
        """测试注册时用户名已存在"""
        # 准备
        existing_user = User(
            username=Username(value="existinguser"),
            email=Email(value="existing@example.com"),
            hashed_password=HashedPassword(value="hashed_password")
        )
        mock_unit_of_work.users.find_by_username.return_value = existing_user
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        command = RegisterUserCommand(
            username="existinguser",
            email="new@example.com",
            password="Test@123456"
        )
        
        # 执行并验证异常
        with pytest.raises(UserAlreadyExistsError, match="用户名已存在"):
            await service.register_user(command)
        
        # 验证未保存
        mock_unit_of_work.users.save.assert_not_called()
        mock_unit_of_work.commit.assert_not_called()
    
    async def test_register_user_email_exists(self, mock_unit_of_work, password_service, jwt_service):
        """测试注册时邮箱已存在"""
        # 准备
        existing_user = User(
            username=Username(value="otheruser"),
            email=Email(value="existing@example.com"),
            hashed_password=HashedPassword(value="hashed_password")
        )
        mock_unit_of_work.users.find_by_username.return_value = None
        mock_unit_of_work.users.find_by_email.return_value = existing_user
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        command = RegisterUserCommand(
            username="newuser",
            email="existing@example.com",
            password="Test@123456"
        )
        
        # 执行并验证异常
        with pytest.raises(UserAlreadyExistsError, match="邮箱已被注册"):
            await service.register_user(command)
    
    async def test_login_success(self, mock_unit_of_work, password_service, jwt_service, test_user):
        """测试成功登录"""
        # 准备
        test_user.activate()  # 激活用户
        mock_unit_of_work.users.find_by_username.return_value = test_user
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        command = LoginUserCommand(
            username_or_email="testuser",
            password="Test@123456",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        # 执行
        result = await service.login(command)
        
        # 验证
        assert "access_token" in result
        assert "refresh_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"
        assert "user" in result
        assert result["user"]["username"] == "testuser"
        
        # 验证用户登录记录
        assert test_user.last_login_at is not None
        assert test_user.login_count == 1
        
        # 验证调用
        mock_unit_of_work.users.save.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()
    
    async def test_login_invalid_username(self, mock_unit_of_work, password_service, jwt_service):
        """测试无效用户名登录"""
        # 准备
        mock_unit_of_work.users.find_by_username.return_value = None
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        command = LoginUserCommand(
            username_or_email="nonexistent",
            password="Test@123456",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        # 执行并验证异常
        with pytest.raises(InvalidCredentialsError):
            await service.login(command)
    
    async def test_login_invalid_password(self, mock_unit_of_work, password_service, jwt_service, test_user):
        """测试无效密码登录"""
        # 准备
        test_user.activate()
        mock_unit_of_work.users.find_by_username.return_value = test_user
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        command = LoginUserCommand(
            username_or_email="testuser",
            password="WrongPassword123!",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        # 执行并验证异常
        with pytest.raises(InvalidCredentialsError):
            await service.login(command)
    
    async def test_login_inactive_user(self, mock_unit_of_work, password_service, jwt_service, test_user):
        """测试未激活用户登录"""
        # 准备 - test_user默认状态是PENDING_VERIFICATION
        mock_unit_of_work.users.find_by_username.return_value = test_user
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        command = LoginUserCommand(
            username_or_email="testuser",
            password="Test@123456",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        # 执行并验证异常
        with pytest.raises(InvalidCredentialsError, match="账户未激活"):
            await service.login(command)
    
    async def test_get_user_profile(self, mock_unit_of_work, password_service, jwt_service, test_user):
        """测试获取用户资料"""
        # 准备
        mock_unit_of_work.users.find_by_id.return_value = test_user
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        # 执行
        result = await service.get_user_profile(test_user.id)
        
        # 验证
        assert result["id"] == str(test_user.id)
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert result["profile"] is not None
    
    async def test_get_user_profile_not_found(self, mock_unit_of_work, password_service, jwt_service):
        """测试获取不存在的用户资料"""
        # 准备
        mock_unit_of_work.users.find_by_id.return_value = None
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        # 执行并验证异常
        with pytest.raises(UserNotFoundError):
            await service.get_user_profile(uuid4())
    
    async def test_update_profile(self, mock_unit_of_work, password_service, jwt_service, test_user):
        """测试更新用户资料"""
        # 准备
        mock_unit_of_work.users.find_by_id.return_value = test_user
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        command = UpdateUserProfileCommand(
            display_name="Updated Name",
            bio="Updated bio"
        )
        
        # 执行
        result = await service.update_profile(command)
        
        # 验证
        assert result["profile"]["display_name"] == "Updated Name"
        assert result["profile"]["bio"] == "Updated bio"
        
        # 验证调用
        mock_unit_of_work.users.save.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()
    
    async def test_change_password(self, mock_unit_of_work, password_service, jwt_service, test_user):
        """测试修改密码"""
        # 准备
        mock_unit_of_work.users.find_by_id.return_value = test_user
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        command = ChangePasswordCommand(
            old_password="Test@123456",
            new_password="NewTest@123456"
        )
        
        # 执行
        await service.change_password(command)
        
        # 验证
        mock_unit_of_work.users.save.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()
        
        # 验证密码已更新
        assert test_user.password_changed_at is not None
    
    async def test_change_password_wrong_old_password(self, mock_unit_of_work, password_service, jwt_service, test_user):
        """测试使用错误的旧密码修改密码"""
        # 准备
        mock_unit_of_work.users.find_by_id.return_value = test_user
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        command = ChangePasswordCommand(
            old_password="WrongOldPassword@123",
            new_password="NewTest@123456"
        )
        
        # 执行并验证异常
        with pytest.raises(InvalidCredentialsError, match="旧密码不正确"):
            await service.change_password(command)
        
        # 验证未保存
        mock_unit_of_work.users.save.assert_not_called()
    
    async def test_activate_user(self, mock_unit_of_work, password_service, jwt_service, test_user):
        """测试激活用户"""
        # 准备
        mock_unit_of_work.users.find_by_id.return_value = test_user
        
        service = UserApplicationService(
            unit_of_work=mock_unit_of_work,
            password_service=password_service,
            jwt_service=jwt_service
        )
        
        # 执行
        await service.activate_user(test_user.id, "valid_token")
        
        # 验证
        assert test_user.status == UserStatus.ACTIVE
        assert test_user.email_verified is True
        
        # 验证调用
        mock_unit_of_work.users.save.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()