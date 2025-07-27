"""用户应用服务单元测试"""

from uuid import uuid4

import pytest

from bounded_contexts.user_management.application.commands.user_commands import (
    RegisterUserCommand, LoginUserCommand, UpdateUserProfileCommand, ChangePasswordCommand
)
from bounded_contexts.user_management.application.services.user_application_service import (
    UserApplicationService
)
from shared_kernel.application.exceptions import (
    UserAlreadyExistsException, InvalidCredentialsException, UserNotFoundException
)
from shared_kernel.domain.value_objects import (
    UserStatus
)


@pytest.mark.asyncio
class TestUserApplicationService:
    """用户应用服务测试"""

    async def test_register_user_success(self, mock_user_repository, password_service, jwt_service):
        """测试成功注册用户"""
        # 准备
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = False

        # Mock save方法来返回传入的用户对象
        async def mock_save(user):
            return user

        mock_user_repository.save.side_effect = mock_save

        service = UserApplicationService(
            user_repository=mock_user_repository,
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
        assert result.username.value == "newuser"
        assert result.email.value == "new@example.com"
        # TODO: 等邮箱验证服务接入后，改回PENDING_VERIFICATION
        assert result.status == UserStatus.ACTIVE
        assert result.id is not None

        # 验证调用
        mock_user_repository.save.assert_called_once()

    async def test_register_user_username_exists(self, mock_user_repository, password_service, jwt_service):
        """测试注册时用户名已存在"""
        # 准备
        mock_user_repository.exists_by_username.return_value = True

        service = UserApplicationService(
            user_repository=mock_user_repository,
            password_service=password_service,
            jwt_service=jwt_service
        )

        command = RegisterUserCommand(
            username="existinguser",
            email="new@example.com",
            password="Test@123456"
        )

        # 执行并验证异常
        from shared_kernel.application.exceptions import UserAlreadyExistsException
        with pytest.raises(UserAlreadyExistsException):
            await service.register_user(command)

        # 验证未保存
        mock_user_repository.save.assert_not_called()

    async def test_register_user_email_exists(self, mock_user_repository, password_service, jwt_service):
        """测试注册时邮箱已存在"""
        # 准备
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.exists_by_email.return_value = True

        service = UserApplicationService(
            user_repository=mock_user_repository,
            password_service=password_service,
            jwt_service=jwt_service
        )

        command = RegisterUserCommand(
            username="newuser",
            email="existing@example.com",
            password="Test@123456"
        )

        # 执行并验证异常
        with pytest.raises(UserAlreadyExistsException):
            await service.register_user(command)

    async def test_login_success(self, mock_user_repository, password_service, jwt_service, test_user):
        """测试成功登录"""
        # 准备
        # test_user已经是ACTIVE状态，不需要再激活
        mock_user_repository.get_by_username.return_value = test_user

        service = UserApplicationService(
            user_repository=mock_user_repository,
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
        result = await service.login_user(command)

        # 验证
        assert "access_token" in result
        assert "refresh_token" in result
        assert "token_type" in result
        assert result["token_type"] == "Bearer"
        assert "user" in result
        assert result["user"].username.value == "testuser"

        # 验证用户登录记录
        assert test_user.last_login_at is not None

        # 验证调用
        mock_user_repository.save.assert_called_once()

    async def test_login_invalid_username(self, mock_user_repository, password_service, jwt_service):
        """测试无效用户名登录"""
        # 准备
        mock_user_repository.get_by_username.return_value = None

        service = UserApplicationService(
            user_repository=mock_user_repository,
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
        with pytest.raises(InvalidCredentialsException):
            await service.login_user(command)

    async def test_login_invalid_password(self, mock_user_repository, password_service, jwt_service, test_user):
        """测试无效密码登录"""
        # 准备
        test_user.activate()
        mock_user_repository.get_by_username.return_value = test_user

        service = UserApplicationService(
            user_repository=mock_user_repository,
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
        with pytest.raises(InvalidCredentialsException):
            await service.login_user(command)

    async def test_login_inactive_user(self, mock_user_repository, password_service, jwt_service, test_user):
        """测试未激活用户登录"""
        # TODO: 暂时跳过未激活用户抛异常的测试，等邮箱验证服务接入后再处理
        # 当前实现中已注释掉邮箱验证检查，允许PENDING_VERIFICATION状态用户登录
        pytest.skip("邮箱验证服务未接入，暂时跳过此测试")

    async def test_get_user_profile(self, mock_user_repository, password_service, jwt_service, test_user):
        """测试获取用户资料"""
        # 准备
        mock_user_repository.get_by_id.return_value = test_user

        service = UserApplicationService(
            user_repository=mock_user_repository,
            password_service=password_service,
            jwt_service=jwt_service
        )

        # 执行
        result = await service.get_user_profile(test_user.id)

        # 验证
        assert result["id"] == str(test_user.id)
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert result["profile"] is None  # test_user没有profile

    async def test_get_user_profile_not_found(self, mock_user_repository, password_service, jwt_service):
        """测试获取不存在的用户资料"""
        # 准备
        mock_user_repository.get_by_id.return_value = None

        service = UserApplicationService(
            user_repository=mock_user_repository,
            password_service=password_service,
            jwt_service=jwt_service
        )

        # 执行并验证异常
        with pytest.raises(UserNotFoundException):
            await service.get_user_profile(uuid4())

    async def test_update_profile(self, mock_user_repository, password_service, jwt_service, test_user):
        """测试更新用户资料"""
        # 准备
        mock_user_repository.get_by_id.return_value = test_user

        # Mock save方法返回用户对象
        async def mock_save(user):
            return user

        mock_user_repository.save.side_effect = mock_save

        service = UserApplicationService(
            user_repository=mock_user_repository,
            password_service=password_service,
            jwt_service=jwt_service
        )

        command = UpdateUserProfileCommand(
            display_name="Updated Name",
            bio="Updated bio"
        )

        # 执行
        result = await service.update_user_profile(test_user.id, command)

        # 验证
        assert result.profile.display_name == "Updated Name"
        assert result.profile.bio == "Updated bio"

        # 验证调用
        mock_user_repository.save.assert_called_once()

    async def test_change_password(self, mock_user_repository, password_service, jwt_service, test_user):
        """测试修改密码"""
        # 准备
        mock_user_repository.get_by_id.return_value = test_user

        service = UserApplicationService(
            user_repository=mock_user_repository,
            password_service=password_service,
            jwt_service=jwt_service
        )

        command = ChangePasswordCommand(
            old_password="Test@123456",
            new_password="NewTest@123456"
        )

        # 执行
        await service.change_password(test_user.id, command)

        # 验证
        mock_user_repository.save.assert_called_once()

        # 验证密码已更新
        assert test_user.password_changed_at is not None

    async def test_change_password_wrong_old_password(self, mock_user_repository, password_service, jwt_service,
                                                      test_user):
        """测试使用错误的旧密码修改密码"""
        # 准备
        mock_user_repository.get_by_id.return_value = test_user

        service = UserApplicationService(
            user_repository=mock_user_repository,
            password_service=password_service,
            jwt_service=jwt_service
        )

        command = ChangePasswordCommand(
            old_password="WrongOldPassword@123",
            new_password="NewTest@123456"
        )

        # 执行并验证异常
        with pytest.raises(InvalidCredentialsException, match="原密码错误"):
            await service.change_password(test_user.id, command)

        # 验证未保存
        mock_user_repository.save.assert_not_called()

    async def test_activate_user(self, mock_user_repository, password_service, jwt_service, test_user):
        """测试激活用户"""
        # 准备
        mock_user_repository.get_by_id.return_value = test_user

        service = UserApplicationService(
            user_repository=mock_user_repository,
            password_service=password_service,
            jwt_service=jwt_service
        )

        # 执行
        await service.activate_user(test_user.id)

        # 验证
        assert test_user.status == UserStatus.ACTIVE

        # 验证调用
        mock_user_repository.save.assert_called_once()
