"""用户仓储SQLAlchemy实现"""

from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.user_profile import UserProfile
from shared_kernel.domain.value_objects import Email, Username, HashedPassword, UserStatus, UserRole
from ..models.user_models import UserModel, UserProfileModel, UserLoginHistoryModel, PasswordResetTokenModel, EmailVerificationTokenModel


class SQLAlchemyUserRepository(UserRepository):
    """用户仓储SQLAlchemy实现"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, user: User) -> User:
        """保存用户"""
        # 查询现有用户
        if user.id:
            stmt = select(UserModel).options(
                selectinload(UserModel.profile)
            ).where(UserModel.id == user.id)
            result = await self._session.execute(stmt)
            db_user = result.scalar_one_or_none()
            
            if db_user:
                # 更新现有用户
                db_user.username = user.username.value
                db_user.email = user.email.value
                # 只有当密码真正发生变化时才更新password_changed_at
                if db_user.hashed_password != user.hashed_password.value:
                    db_user.password_changed_at = user.password_changed_at
                db_user.hashed_password = user.hashed_password.value
                db_user.status = user.status.value
                db_user.role = user.role.value
                db_user.last_login_at = user.last_login_at
                db_user.updated_at = user.updated_at
            else:
                # 创建新用户
                db_user = self._domain_to_model(user)
                self._session.add(db_user)
        else:
            # 创建新用户
            db_user = self._domain_to_model(user)
            self._session.add(db_user)
        
        await self._session.flush()  # 获取数据库分配的 id
        
        # 更新领域对象的 id（如果是新创建的）
        if user.id is None:
            user.id = db_user.id
        
        # 处理用户资料
        if user.profile:
            await self._save_user_profile(db_user, user.profile)
        
        await self._session.refresh(db_user)
        
        # 重新查询以确保 profile 关系被正确预加载
        stmt = select(UserModel).options(
            selectinload(UserModel.profile)
        ).where(UserModel.id == db_user.id)
        result = await self._session.execute(stmt)
        refreshed_user = result.scalar_one()
        
        # 返回更新后的领域对象
        return await self._model_to_domain(refreshed_user)
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        stmt = select(UserModel).options(
            selectinload(UserModel.profile)
        ).where(UserModel.id == user_id)
        
        result = await self._session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        return await self._model_to_domain(db_user) if db_user else None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        stmt = select(UserModel).options(
            selectinload(UserModel.profile)
        ).where(func.lower(UserModel.username) == func.lower(username))
        
        result = await self._session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        return await self._model_to_domain(db_user) if db_user else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        stmt = select(UserModel).options(
            selectinload(UserModel.profile)
        ).where(func.lower(UserModel.email) == func.lower(email))
        
        result = await self._session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        return await self._model_to_domain(db_user) if db_user else None
    
    async def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在"""
        stmt = select(func.count(UserModel.id)).where(
            func.lower(UserModel.username) == func.lower(username)
        )
        result = await self._session.execute(stmt)
        count = result.scalar()
        return count > 0
    
    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在"""
        stmt = select(func.count(UserModel.id)).where(
            func.lower(UserModel.email) == func.lower(email)
        )
        result = await self._session.execute(stmt)
        count = result.scalar()
        return count > 0
    
    async def find_by_status(self, status: str, limit: int = 100) -> List[User]:
        """根据状态查找用户"""
        stmt = select(UserModel).options(
            selectinload(UserModel.profile)
        ).where(UserModel.status == status).limit(limit)
        
        result = await self._session.execute(stmt)
        db_users = result.scalars().all()
        
        result_users = []
        for db_user in db_users:
            domain_user = await self._model_to_domain(db_user)
            result_users.append(domain_user)
        return result_users
    
    async def count_by_status(self, status: str) -> int:
        """统计指定状态的用户数量"""
        stmt = select(func.count(UserModel.id)).where(UserModel.status == status)
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def delete(self, user: User) -> bool:
        """删除用户"""
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if db_user:
            await self._session.delete(db_user)
            return True
        return False
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """分页查找所有用户"""
        stmt = select(UserModel).options(
            selectinload(UserModel.profile)
        ).order_by(UserModel.created_at.desc()).offset(skip).limit(limit)
        
        result = await self._session.execute(stmt)
        db_users = result.scalars().all()
        
        result_users = []
        for db_user in db_users:
            domain_user = await self._model_to_domain(db_user)
            result_users.append(domain_user)
        return result_users
    
    async def count(self) -> int:
        """统计用户总数"""
        stmt = select(func.count(UserModel.id))
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def _save_user_profile(self, db_user: UserModel, profile: UserProfile) -> None:
        """保存用户资料"""
        # 查询现有的用户资料，避免直接访问关系属性
        stmt = select(UserProfileModel).where(UserProfileModel.user_id == db_user.id)
        result = await self._session.execute(stmt)
        existing_profile = result.scalar_one_or_none()
        
        if existing_profile:
            # 更新现有资料
            existing_profile.display_name = profile.display_name
            existing_profile.avatar_url = profile.avatar_url
            existing_profile.bio = profile.bio
            existing_profile.timezone = profile.timezone
            existing_profile.language = profile.language
            existing_profile.notification_preferences = profile.notification_preferences
        else:
            # 创建新资料
            db_profile = UserProfileModel(
                user_id=db_user.id,
                display_name=profile.display_name,
                avatar_url=profile.avatar_url,
                bio=profile.bio,
                timezone=profile.timezone,
                language=profile.language,
                notification_preferences=profile.notification_preferences
            )
            self._session.add(db_profile)
    
    def _domain_to_model(self, user: User) -> UserModel:
        """领域对象转换为数据库模型"""
        model_data = {
            "username": user.username.value,
            "email": user.email.value,
            "hashed_password": user.hashed_password.value,
            "status": user.status.value,
            "role": user.role.value,
            "last_login_at": user.last_login_at,
            "password_changed_at": user.password_changed_at,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        
        # 只有当user.id存在且不为None时才设置id
        if user.id is not None:
            model_data["id"] = user.id
            
        return UserModel(**model_data)
    
    async def _model_to_domain(self, db_user: UserModel) -> User:
        """数据库模型转换为领域对象"""
        profile = None
        if db_user.profile:
            profile = UserProfile(
                display_name=db_user.profile.display_name,
                avatar_url=db_user.profile.avatar_url,
                bio=db_user.profile.bio,
                timezone=db_user.profile.timezone,
                language=db_user.profile.language,
                notification_preferences=db_user.profile.notification_preferences
            )
        
        user = User(
            id=db_user.id,
            username=Username(value=db_user.username),
            email=Email(value=db_user.email),
            hashed_password=HashedPassword(value=db_user.hashed_password),
            status=UserStatus(db_user.status),
            role=UserRole(db_user.role),
            last_login_at=db_user.last_login_at,
            password_changed_at=db_user.password_changed_at,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            version=1,
            profile=profile
        )
        
        # 清除事件，避免重复处理
        user.clear_domain_events()
        
        return user
    
    async def get_login_history(self, user_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """获取用户登录历史"""
        try:
            # 计算总数
            count_stmt = select(func.count(UserLoginHistoryModel.id)).where(
                UserLoginHistoryModel.user_id == user_id
            )
            total_result = await self._session.execute(count_stmt)
            total = total_result.scalar() or 0
            
            # 分页查询
            offset = (page - 1) * limit
            stmt = select(UserLoginHistoryModel).where(
                UserLoginHistoryModel.user_id == user_id
            ).order_by(
                UserLoginHistoryModel.created_at.desc()
            ).offset(offset).limit(limit)
            
            result = await self._session.execute(stmt)
            records = result.scalars().all()
            
            return {
                "items": records,
                "total": total
            }
            
        except Exception as e:
            # 如果表不存在或查询失败，返回空结果
            return {"items": [], "total": 0}
    
    async def save_login_history(self, login_record: Dict[str, Any]) -> None:
        """保存登录历史记录"""
        try:
            db_record = UserLoginHistoryModel(
                user_id=login_record["user_id"],
                ip_address=login_record["ip_address"],
                user_agent=login_record["user_agent"],
                login_status="success" if login_record["success"] else "failed",
                location_info={"city": login_record.get("location", "未知位置")},
                created_at=login_record["login_at"]
            )
            
            self._session.add(db_record)
            await self._session.flush()
            
        except Exception as e:
            # 登录历史记录失败不应该影响主流程
            print(f"Failed to save login history: {str(e)}")
            pass
    
    async def find_users_paginated(
        self, 
        page: int = 1, 
        page_size: int = 20,
        status: Optional[str] = None,
        role: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """分页查询用户"""
        
        # 构建查询条件
        conditions = []
        
        if status:
            conditions.append(UserModel.status == status)
        
        if role:
            conditions.append(UserModel.role == role)
        
        if search:
            search_term = f"%{search}%"
            conditions.append(
                or_(
                    UserModel.username.ilike(search_term),
                    UserModel.email.ilike(search_term)
                )
            )
        
        # 计算总数
        count_stmt = select(func.count(UserModel.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # 分页查询
        offset = (page - 1) * page_size
        stmt = select(UserModel).options(
            selectinload(UserModel.profile)
        ).order_by(UserModel.created_at.desc())
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
            
        stmt = stmt.offset(offset).limit(page_size)
        
        result = await self._session.execute(stmt)
        db_users = result.scalars().all()
        
        # 转换为领域对象
        users = []
        for db_user in db_users:
            domain_user = await self._model_to_domain(db_user)
            users.append(domain_user)
        
        return users, total
    
    async def save_password_reset_token(self, user_id: int, token: str, expires_at) -> None:
        """保存密码重置token"""
        try:
            # 删除用户现有的未使用的重置token
            delete_stmt = text("""
                DELETE FROM password_reset_tokens 
                WHERE user_id = :user_id AND is_used = false
            """)
            await self._session.execute(delete_stmt, {"user_id": user_id})
            
            # 创建新的重置token
            reset_token = PasswordResetTokenModel(
                user_id=user_id,
                token=token,
                expires_at=expires_at,
                is_used=False
            )
            
            self._session.add(reset_token)
            await self._session.flush()
            
        except Exception as e:
            print(f"Failed to save password reset token: {str(e)}")
            raise
    
    async def get_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """获取密码重置token信息"""
        try:
            stmt = select(PasswordResetTokenModel).where(
                PasswordResetTokenModel.token == token
            )
            result = await self._session.execute(stmt)
            reset_token = result.scalar_one_or_none()
            
            if reset_token:
                return {
                    "user_id": reset_token.user_id,
                    "expires_at": reset_token.expires_at,
                    "used": reset_token.is_used
                }
            return None
            
        except Exception as e:
            print(f"Failed to get password reset token: {str(e)}")
            return None
    
    async def mark_password_reset_token_used(self, token: str) -> None:
        """标记密码重置token为已使用"""
        try:
            stmt = text("""
                UPDATE password_reset_tokens 
                SET is_used = true 
                WHERE token = :token
            """)
            await self._session.execute(stmt, {"token": token})
            await self._session.flush()
            
        except Exception as e:
            print(f"Failed to mark password reset token as used: {str(e)}")
            pass
    
    async def save_email_verification_token(self, user_id: int, token: str, expires_at) -> None:
        """保存邮箱验证token"""
        try:
            # 删除用户现有的未使用的验证token
            delete_stmt = text("""
                DELETE FROM email_verification_tokens 
                WHERE user_id = :user_id AND is_verified = false
            """)
            await self._session.execute(delete_stmt, {"user_id": user_id})
            
            # 获取用户邮箱
            user = await self.get_by_id(user_id)
            if not user:
                raise ValueError(f"User not found: {user_id}")
            
            # 创建新的验证token
            verification_token = EmailVerificationTokenModel(
                user_id=user_id,
                token=token,
                email=user.email.value,
                expires_at=expires_at,
                is_verified=False
            )
            
            self._session.add(verification_token)
            await self._session.flush()
            
        except Exception as e:
            print(f"Failed to save email verification token: {str(e)}")
            raise
    
    async def get_email_verification_token(self, token: str) -> Optional[Dict[str, Any]]:
        """获取邮箱验证token信息"""
        try:
            stmt = select(EmailVerificationTokenModel).where(
                EmailVerificationTokenModel.token == token
            )
            result = await self._session.execute(stmt)
            verification_token = result.scalar_one_or_none()
            
            if verification_token:
                return {
                    "user_id": verification_token.user_id,
                    "email": verification_token.email,
                    "expires_at": verification_token.expires_at,
                    "is_verified": verification_token.is_verified
                }
            return None
            
        except Exception as e:
            print(f"Failed to get email verification token: {str(e)}")
            return None
    
    async def mark_email_verification_token_used(self, token: str) -> None:
        """标记邮箱验证token为已使用"""
        try:
            stmt = text("""
                UPDATE email_verification_tokens 
                SET is_verified = true, verified_at = NOW()
                WHERE token = :token
            """)
            await self._session.execute(stmt, {"token": token})
            await self._session.flush()
            
        except Exception as e:
            print(f"Failed to mark email verification token as used: {str(e)}")
            pass