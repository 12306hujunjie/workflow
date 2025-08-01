"""用户应用服务"""

import re
import secrets
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.user_profile import UserProfile
from shared_kernel.domain.value_objects import UserStatus, UserRole, Username, Email
from shared_kernel.application.exceptions import (
    UserAlreadyExistsException, UserNotFoundException, InvalidCredentialsException,
    ValidationException, AuthorizationException
)
from ...infrastructure.auth.password_service import PasswordService
from ...infrastructure.auth.jwt_service import JWTService
from shared_kernel.infrastructure.email_service import EmailService
from shared_kernel.infrastructure.verification_code_service import VerificationCodeService
from shared_kernel.infrastructure.redis_service import RedisService
from shared_kernel.infrastructure.rate_limit_service import RateLimitService
from ..commands.user_commands import (
    RegisterUserCommand, LoginUserCommand, UpdateUserProfileCommand,
    ChangePasswordCommand, ResetPasswordCommand
)


class UserApplicationService:
    """用户应用服务"""
    
    # Email validation regex pattern - practical and secure
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9._%+-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$')
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        jwt_service: JWTService,
        email_service: EmailService,
        verification_code_service: Optional[VerificationCodeService] = None,
        rate_limit_service: Optional[RateLimitService] = None
    ):
        self._user_repository = user_repository
        self._password_service = password_service
        self._jwt_service = jwt_service
        self._email_service = email_service
        self._verification_code_service = verification_code_service
        self._rate_limit_service = rate_limit_service
    
    def _validate_email(self, email: str) -> None:
        """验证邮箱格式 - 严格验证，与Pydantic EmailStr一致"""
        if not email or not isinstance(email, str):
            raise ValidationException("邮箱地址不能为空")
        
        email = email.strip()
        
        # 基本格式检查
        if not email or '@' not in email or email.count('@') != 1:
            raise ValidationException("请输入有效的邮箱地址")
        
        # 分割邮箱地址
        local, domain = email.split('@')
        
        # 验证本地部分（@前面的部分）
        if not local or len(local) > 64:
            raise ValidationException("请输入有效的邮箱地址")
        
        # 验证域名部分（@后面的部分）
        if not domain or len(domain) > 253 or '.' not in domain:
            raise ValidationException("请输入有效的邮箱地址")
        
        # 验证域名格式
        domain_parts = domain.split('.')
        if len(domain_parts) < 2:
            raise ValidationException("请输入有效的邮箱地址")
        
        # 检查每个域名部分
        for part in domain_parts:
            if not part or len(part) > 63:
                raise ValidationException("请输入有效的邮箱地址")
            # 域名部分只能包含字母、数字、连字符
            if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$', part):
                raise ValidationException("请输入有效的邮箱地址")
        
        # 检查顶级域名
        tld = domain_parts[-1]
        if len(tld) < 2 or not tld.isalpha():
            raise ValidationException("请输入有效的邮箱地址")
        
        # 验证本地部分格式
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9._%+-]*[a-zA-Z0-9])?$', local):
            raise ValidationException("请输入有效的邮箱地址")
        
        # Additional length check
        if len(email) > 254:  # RFC 5321 limit
            raise ValidationException("邮箱地址过长")
    
    async def register_user(self, command: RegisterUserCommand) -> User:
        """注册新用户"""
        # 验证邮箱格式
        self._validate_email(command.email)
        
        # 验证用户名是否已存在
        user_repository: UserRepository = self._user_repository

        if user_repository and await self._user_repository.exists_by_username(command.username):
            raise UserAlreadyExistsException("username", command.username)
        
        # 验证邮箱是否已存在
        if user_repository and await self._user_repository.exists_by_email(command.email):
            raise UserAlreadyExistsException("email", command.email)
        
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
        
        # 发送邮箱验证邮件（使用验证码）
        if self._verification_code_service:
            # 新的验证码模式
            verification_code = await self._verification_code_service.generate_and_store_code(
                email=saved_user.email.value,
                purpose="register"
            )
            
            # 发送验证码邮件
            await self._email_service.send_verification_code_email(
                to_email=saved_user.email.value,
                username=saved_user.username.value,
                code=verification_code,
                purpose="register"
            )
        else:
            # 兼容旧的token模式
            verification_token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)  # 24小时过期
            
            await self._user_repository.save_email_verification_token(
                user_id=saved_user.id,
                token=verification_token,
                expires_at=expires_at
            )
            
            # 发送验证邮件
            await self._email_service.send_verification_email(
                to_email=saved_user.email.value,
                username=saved_user.username.value,
                token=verification_token
            )
        
        return saved_user
    
    async def login_user(self, command: LoginUserCommand) -> Dict[str, Any]:
        """用户登录"""
        # 根据用户名或邮箱查找用户
        if "@" in command.username_or_email:
            # 直接使用原始邮箱值进行查找
            user = await self._user_repository.get_by_email(command.username_or_email)
        else:
            # 直接使用原始用户名值进行查找
            user = await self._user_repository.get_by_username(command.username_or_email)
        
        if not user:
            raise InvalidCredentialsException()
        
        # 验证密码
        if not self._password_service.verify_password(command.password, user.hashed_password.value):
            raise InvalidCredentialsException()
        
        # 检查用户是否可以登录
        if not user.can_login():
            # 邮箱验证检查
            if user.status == UserStatus.PENDING_VERIFICATION:
                raise AuthorizationException("账户待验证，请先验证邮箱")
            if user.status == UserStatus.BANNED:
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
    
    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """获取用户资料"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id=str(user_id))
        
        profile_data = None
        if user.profile:
            profile_data = {
                "display_name": user.profile.display_name,
                "bio": user.profile.bio,
                "avatar_url": user.profile.avatar_url
            }
        
        return {
            "id": str(user.id),
            "username": user.username.value,
            "email": user.email.value,
            "status": user.status.value,
            "role": user.role.value,
            "last_login_at": user.last_login_at,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "profile": profile_data
        }
    
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
        payload = await self._jwt_service.verify_refresh_token(refresh_token)
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
        return await self._user_repository.find_users_paginated(
            page=page,
            page_size=page_size,
            status=status,
            role=role,
            search=search
        )
    
    async def logout_user(self, user_id: int, access_token: str, refresh_token: Optional[str] = None) -> None:
        """用户登出"""
        # 验证access token是否有效
        try:
            payload = await self._jwt_service.verify_access_token(access_token)
            if payload.get("user_id") != user_id:
                raise AuthorizationException("Token用户ID不匹配")
        except ValueError as e:
            raise AuthorizationException(f"无效的access token: {str(e)}")
        
        # 将access token添加到黑名单
        await self._jwt_service.blacklist_token(access_token)
        
        # 如果提供了refresh token，也将其添加到黑名单
        if refresh_token:
            try:
                # 验证refresh token是否有效且属于同一用户
                refresh_payload = await self._jwt_service.verify_refresh_token(refresh_token)
                if refresh_payload.get("user_id") == user_id:
                    await self._jwt_service.blacklist_token(refresh_token)
            except ValueError:
                # refresh token无效，忽略错误继续执行
                pass
    
    async def forgot_password(self, email: str) -> str:
        """忘记密码 - 发送重置邮件"""
        # 验证邮箱格式
        self._validate_email(email)
        
        user = await self._user_repository.get_by_email(email)
        if not user:
            # 为了安全，即使用户不存在也返回成功消息
            return "如果该邮箱存在，重置密码验证码已发送"
        
        if self._verification_code_service:
            # 新的验证码模式
            reset_code = await self._verification_code_service.generate_and_store_code(
                email=user.email.value,
                purpose="reset_password"
            )
            
            # 发送验证码邮件
            await self._email_service.send_verification_code_email(
                to_email=user.email.value,
                username=user.username.value,
                code=reset_code,
                purpose="reset_password"
            )
            
            return "重置密码验证码已发送，请查收"
        else:
            # 兼容旧的token模式
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)  # 1小时过期
            
            await self._user_repository.save_password_reset_token(
                user_id=user.id,
                token=reset_token,
                expires_at=expires_at
            )
            
            # 发送密码重置邮件
            await self._email_service.send_password_reset_email(
                to_email=user.email.value,
                username=user.username.value,
                token=reset_token
            )
            
            return "重置密码邮件已发送，请查收"
    
    async def reset_password(self, token: str, new_password: str) -> None:
        """重置密码"""
        # 验证重置token
        reset_data = await self._user_repository.get_password_reset_token(token)
        if not reset_data:
            raise ValidationException("无效的重置令牌")
        
        # 检查token是否过期
        if reset_data['expires_at'] < datetime.now(timezone.utc):
            raise ValidationException("重置令牌已过期")
        
        # 检查token是否已使用
        if reset_data['used']:
            raise ValidationException("重置令牌已使用")
        
        # 获取用户
        user = await self._user_repository.get_by_id(reset_data['user_id'])
        if not user:
            raise UserNotFoundException(user_id=str(reset_data['user_id']))
        
        # 验证新密码强度（基本验证）
        if len(new_password) < 8:
            raise ValidationException("密码长度至少需要8个字符")
        
        # 更新密码
        hashed_password = self._password_service.hash_password(new_password)
        user.update_password(hashed_password)
        await self._user_repository.save(user)
        
        # 标记token为已使用
        await self._user_repository.mark_password_reset_token_used(token)
    
    async def verify_code_only(self, email: str, code: str, purpose: str) -> None:
        """纯验证码验证（不检查用户存在性）"""
        # 验证邮箱格式
        self._validate_email(email)
        
        if not self._verification_code_service:
            raise ValidationException("验证码服务未启用")
        
        # 验证验证码
        is_valid = await self._verification_code_service.verify_code(
            email=email,
            purpose=purpose,
            code=code
        )
        
        if not is_valid:
            raise ValidationException("验证码错误或已过期")
    
    async def verify_email_with_code(self, email: str, code: str) -> None:
        """使用验证码验证邮箱并激活用户（仅用于邮箱验证激活场景）"""
        # 验证邮箱格式
        self._validate_email(email)
        
        # 先验证验证码
        await self.verify_code_only(email, code, "register")
        
        # 获取用户并激活
        user = await self._user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundException(f"邮箱 {email} 对应的用户不存在")
        
        # 激活用户账户
        user.activate()
        await self._user_repository.save(user)
    
    async def reset_password_with_code(self, email: str, code: str, new_password: str) -> None:
        """使用验证码重置密码"""
        # 验证邮箱格式
        self._validate_email(email)
        
        if not self._verification_code_service:
            raise ValidationException("验证码服务未启用")
        
        # 先验证验证码
        await self.verify_code_only(email, code, "reset_password")
        
        # 获取用户
        user = await self._user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundException(f"邮箱 {email} 对应的用户不存在")
        
        # 验证新密码强度（基本验证）
        if len(new_password) < 8:
            raise ValidationException("密码长度至少需要8个字符")
        
        # 更新密码
        hashed_password = self._password_service.hash_password(new_password)
        user.update_password(hashed_password)
        await self._user_repository.save(user)
    
    async def resend_verification_code(self, email: str, purpose: str) -> str:
        """重新发送验证码"""
        # 验证邮箱格式
        self._validate_email(email)
        
        if not self._verification_code_service:
            raise ValidationException("验证码服务未启用")
        
        # 检查用户是否存在
        user = await self._user_repository.get_by_email(email)
        if not user:
            return "如果该邮箱存在，验证码已重新发送"
        
        # 生成新的验证码（会覆盖旧的）
        code = await self._verification_code_service.generate_and_store_code(
            email=email,
            purpose=purpose
        )
        
        # 发送验证码邮件
        await self._email_service.send_verification_code_email(
            to_email=email,
            username=user.username.value,
            code=code,
            purpose=purpose
        )
        
        return "验证码已重新发送，请查收"

    async def send_verification_code_with_rate_limit(
        self, 
        email: str, 
        purpose: str, 
        client_ip: str
    ) -> str:
        """发送验证码（带频率限制）"""
        # 验证邮箱格式
        self._validate_email(email)
        
        if not self._verification_code_service:
            raise ValidationException("验证码服务未启用")
        
        if not self._rate_limit_service:
            raise ValidationException("频率限制服务未启用")
        
        # 应用频率限制（IP + 邮箱 + 接口名，3分钟限制）
        endpoint = f"send_verification_code_{purpose}"
        await self._rate_limit_service.apply_rate_limit(
            ip=client_ip,
            email=email,
            endpoint=endpoint,
            limit_seconds=180  # 3分钟
        )
        
        # 生成新的验证码（会覆盖旧的）
        code = await self._verification_code_service.generate_and_store_code(
            email=email,
            purpose=purpose
        )
        
        # 根据用途确定用户名
        username = "用户"  # 默认用户名
        if purpose == "register":
            # 注册时可能用户还不存在，使用默认用户名
            username = "新用户"
        else:
            # 重置密码时，用户应该存在
            user = await self._user_repository.get_by_email(email)
            if user:
                username = user.username.value
        
        # 发送验证码邮件
        await self._email_service.send_verification_code_email(
            to_email=email,
            username=username,
            code=code,
            purpose=purpose
        )
        
        return "验证码已发送，请查收邮件"
    
    async def verify_email(self, token: str) -> None:
        """验证邮箱"""
        # 验证邮箱验证token
        verification_data = await self._user_repository.get_email_verification_token(token)
        if not verification_data:
            raise ValidationException("无效的验证令牌")
        
        # 检查token是否过期
        if verification_data['expires_at'] < datetime.now(timezone.utc):
            raise ValidationException("验证令牌已过期")
        
        # 检查token是否已使用
        if verification_data['is_verified']:
            raise ValidationException("验证令牌已使用")
        
        # 获取用户并激活
        user = await self._user_repository.get_by_id(verification_data['user_id'])
        if not user:
            raise UserNotFoundException(user_id=str(verification_data['user_id']))
        
        # 激活用户账户
        user.activate()
        await self._user_repository.save(user)
        
        # 标记token为已使用
        await self._user_repository.mark_email_verification_token_used(token)
    
    async def resend_verification_email(self, user_id: int) -> None:
        """重新发送验证邮件"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id=str(user_id))
        
        # 检查用户状态
        if user.status == UserStatus.ACTIVE:
            raise ValidationException("用户邮箱已经验证过了")
        
        # 生成新的验证token
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)  # 24小时过期
        
        await self._user_repository.save_email_verification_token(
            user_id=user.id,
            token=verification_token,
            expires_at=expires_at
        )
        
        # 重新发送验证邮件
        await self._email_service.send_verification_email(
            to_email=user.email.value,
            username=user.username.value,
            token=verification_token
        )
    
    async def check_username_availability(self, username: str) -> bool:
        """检查用户名是否可用"""
        return not await self._user_repository.exists_by_username(username)
    
    async def check_email_availability(self, email: str) -> bool:
        """检查邮箱是否可用"""
        # 验证邮箱格式
        self._validate_email(email)
        
        return not await self._user_repository.exists_by_email(email)
    
    async def get_user_activity(self, user_id: int) -> Dict[str, Any]:
        """获取用户活动信息"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id=str(user_id))
        
        # 返回用户活动数据
        return {
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "status": user.status.value,
            "login_count": await self._get_login_count(user_id),
            "profile_completion": self._calculate_profile_completion(user)
        }
    
    async def get_user_login_history(self, user_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """获取用户登录历史"""
        return await self._user_repository.get_login_history(user_id, page, limit)
    
    async def delete_user_account(self, user_id: int) -> None:
        """删除用户账户"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id=str(user_id))
        
        # 软删除 - 将状态设置为已删除
        user.deactivate()  # 使用现有的停用方法
        await self._user_repository.save(user)
    
    async def _get_login_count(self, user_id: int) -> int:
        """获取用户登录次数"""
        try:
            history = await self._user_repository.get_login_history(user_id, 1, 1000)
            return history.get('total', 0)
        except:
            return 0
    
    def _calculate_profile_completion(self, user: User) -> float:
        """计算用户资料完成度"""
        total_fields = 6  # username, email, display_name, bio, avatar_url, timezone
        completed_fields = 2  # username and email are always required
        
        if user.profile:
            if user.profile.display_name:
                completed_fields += 1
            if user.profile.bio:
                completed_fields += 1
            if user.profile.avatar_url:
                completed_fields += 1
            if user.profile.timezone:
                completed_fields += 1
        
        return (completed_fields / total_fields) * 100