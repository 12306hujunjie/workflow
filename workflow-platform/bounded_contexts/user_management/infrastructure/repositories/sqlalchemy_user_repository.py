"""用户仓储SQLAlchemy实现"""

from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.user_profile import UserProfile
from shared_kernel.domain.value_objects import Email, Username, HashedPassword, UserStatus, UserRole
from ..models.user_models import UserModel, UserProfileModel


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