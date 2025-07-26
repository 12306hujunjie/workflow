"""用户应用服务"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
import secrets

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.user_profile import UserProfile
from shared_kernel.domain.value_objects import UserStatus, UserRole
from shared_kernel.application.exceptions import (
    UserAlreadyExistsException, UserNotFoundException, InvalidCredentialsException,
    ValidationException, AuthorizationException
)
from ...infrastructure.auth.password_service import PasswordService
from ...infrastructure.auth.jwt_service import JWTService
from ..commands.user_commands import (
    RegisterUserCommand, LoginUserCommand, UpdateUserProfileCommand,
    ChangePasswordCommand, ResetPasswordCommand
)


class UserApplicationService:
    """用户应用服务"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        jwt_service: JWTService
    ):
        self._user_repository = user_repository
        self._password_service = password_service
        self._jwt_service = jwt_service
    
    async def register_user(self, command: RegisterUserCommand) -> User:
        """注册新用户"""
        # 验证用户名是否已存在
        if await self._user_repository.exists_by_username(command.username):
            raise UserAlreadyExistsException(username=command.username)
        
        # 验证邮箱是否已存在
        if await self._user_repository.exists_by_email(command.email):
            raise UserAlreadyExistsException(email=command.email)
        
        # 验证密码强度
        is_valid, message = self._password_service.validate_password_strength(command.password)
        if not is_valid:
            raise ValidationException(message)
        
        # 加密密码
        hashed_password = self._password_service.hash_password(command.password)
        
        # 创建用户
        user = User.create(
            username=command.username,
            email=command.email,
            hashed_password=hashed_password,
            role=UserRole.USER
        )
        
        # 保存用户
        saved_user = await self._user_repository.save(user)
        
        return saved_user
    
    async def login_user(self, command: LoginUserCommand) -> Dict[str, Any]:
        """用户登录"""
        # 根据用户名或邮箱查找用户
        if "@" in command.username_or_email:
            user = await self._user_repository.get_by_email(command.username_or_email)
        else:
            user = await self._user_repository.get_by_username(command.username_or_email)
        
        if not user:
            raise InvalidCredentialsException()
        
        # 验证密码
        if not self._password_service.verify_password(command.password, user.hashed_password.value):
            raise InvalidCredentialsException()
        
        # 检查用户是否可以登录
        if not user.can_login():
            if user.status == UserStatus.PENDING_VERIFICATION:
                raise AuthorizationException("账户待验证，请先验证邮箱")
            elif user.status == UserStatus.BANNED:
                raise AuthorizationException("账户已被封禁")
            else:
                raise AuthorizationException("账户状态异常，无法登录")
        
        # 记录登录
        user.record_login(command.ip_address)
        await self._user_repository.save(user)
        
        # 创建令牌
        access_token, refresh_token = self._jwt_service.create_token_pair(
            user.id,
            user.username.value,
            user.role.value
        )
        
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self._jwt_service.access_token_expire_minutes * 60
        }
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return await self._user_repository.get_by_id(user_id)
    
    async def update_user_profile(self, user_id: int, command: UpdateUserProfileCommand) -> User:
        """更新用户资料"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id=str(user_id))
        
        # 更新资料
        profile_data = command.dict(exclude_unset=True)
        user.update_profile(profile_data)
        
        # 保存更新
        return await self._user_repository.save(user)
    
    async def change_password(self, user_id: int, command: ChangePasswordCommand) -> None:
        """修改密码"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 验证旧密码
        if not self._password_service.verify_password(command.old_password, user.hashed_password.value):
            raise InvalidCredentialsException("原密码错误")
        
        # 验证新密码强度
        is_valid, message = self._password_service.validate_password_strength(command.new_password)
        if not is_valid:
            raise ValidationException(message)
        
        # 加密新密码
        hashed_password = self._password_service.hash_password(command.new_password)
        
        # 更新密码
        user.update_password(hashed_password)
        await self._user_repository.save(user)
    
    async def activate_user(self, user_id: int) -> User:
        """激活用户"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id=str(user_id))
        
        user.activate()
        return await self._user_repository.save(user)
    
    async def deactivate_user(self, user_id: int) -> User:
        """停用用户"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id=str(user_id))
        
        user.deactivate()
        return await self._user_repository.save(user)
    
    async def ban_user(self, user_id: int) -> User:
        """封禁用户"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id=str(user_id))
        
        user.ban()
        return await self._user_repository.save(user)
    
    async def get_users_by_status(self, status: UserStatus, limit: int = 100) -> List[User]:
        """根据状态获取用户列表"""
        return await self._user_repository.find_by_status(status.value, limit)
    
    async def count_users_by_status(self, status: UserStatus) -> int:
        """统计指定状态的用户数量"""
        return await self._user_repository.count_by_status(status.value)
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新访问令牌"""
        # 验证刷新令牌
        payload = self._jwt_service.verify_refresh_token(refresh_token)
        user_id = payload["user_id"]
        
        # 获取用户信息
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id=str(user_id))
        
        if not user.can_login():
            raise AuthorizationException("用户状态异常，无法刷新令牌")
        
        # 创建新的访问令牌
        access_token = self._jwt_service.create_access_token(
            user.id,
            user.username.value,
            user.role.value
        )
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": self._jwt_service.access_token_expire_minutes * 60
        }
    
    async def get_users_list(
        self, 
        page: int = 1, 
        page_size: int = 20, 
        status: Optional[str] = None,
        role: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """获取用户列表（分页）"""
        # TODO: 实现分页查询逻辑
        # 这里需要在repository中实现相应的方法
        users = await self._user_repository.find_all()
        total = len(users)
        
        # 简单的内存分页（生产环境应该在数据库层面实现）
        start = (page - 1) * page_size
        end = start + page_size
        paginated_users = users[start:end]
        
        return paginated_users, total
    
    async def logout_user(self, user_id: int, token: str) -> None:
        """用户登出"""
        # TODO: 实现token黑名单逻辑
        # 这里需要实现token黑名单机制
        pass
    
    async def forgot_password(self, email: str) -> str:
        """忘记密码 - 发送重置邮件"""
        user = await self._user_repository.get_by_email(email)
        if not user:
            # 为了安全，即使用户不存在也返回成功消息
            return "如果该邮箱存在，重置密码邮件已发送"
        
        # TODO: 生成重置token并发送邮件
        reset_token = secrets.token_urlsafe(32)
        # 这里需要保存reset_token到数据库并设置过期时间
        # 然后发送邮件
        
        return "重置密码邮件已发送，请查收"
    
    async def reset_password(self, token: str, new_password: str) -> None:
        """重置密码"""
        # TODO: 验证重置token并更新密码
        # 1. 验证token是否有效且未过期
        # 2. 获取对应的用户
        # 3. 验证新密码强度
        # 4. 更新密码
        # 5. 删除或标记token为已使用
        pass
    
    async def verify_email(self, token: str) -> None:
        """验证邮箱"""
        # TODO: 实现邮箱验证逻辑
        # 1. 验证token是否有效
        # 2. 获取对应的用户
        # 3. 更新用户状态为已验证
        pass
    
    async def resend_verification_email(self, user_id: int) -> None:
        """重新发送验证邮件"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id=str(user_id))
        
        # TODO: 生成新的验证token并发送邮件
        verification_token = secrets.token_urlsafe(32)
        # 保存token并发送邮件
        pass