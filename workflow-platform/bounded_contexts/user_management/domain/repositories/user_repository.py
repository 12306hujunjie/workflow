"""用户仓储接口"""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.user import User


class UserRepository(ABC):
    """用户仓储接口"""
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """保存用户"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在"""
        pass
    
    @abstractmethod
    async def find_by_status(self, status: str, limit: int = 100) -> List[User]:
        """根据状态查找用户"""
        pass
    
    @abstractmethod
    async def count_by_status(self, status: str) -> int:
        """统计指定状态的用户数量"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """删除用户"""
        pass