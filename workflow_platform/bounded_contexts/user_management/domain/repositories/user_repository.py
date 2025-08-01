"""用户仓储接口"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

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
    async def delete(self, user: User) -> bool:
        """删除用户"""
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """查找所有用户"""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """统计用户总数"""
        pass
    
    @abstractmethod
    async def get_login_history(self, user_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """获取用户登录历史"""
        pass
        
    @abstractmethod
    async def save_login_history(self, login_record: Dict[str, Any]) -> None:
        """保存登录历史记录"""
        pass
        
    @abstractmethod
    async def find_users_paginated(
        self, 
        page: int = 1, 
        page_size: int = 20,
        status: Optional[str] = None,
        role: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """分页查询用户"""
        pass
    
    @abstractmethod
    async def save_password_reset_token(self, user_id: int, token: str, expires_at) -> None:
        """保存密码重置token"""
        pass
        
    @abstractmethod  
    async def get_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """获取密码重置token信息"""
        pass
        
    @abstractmethod
    async def mark_password_reset_token_used(self, token: str) -> None:
        """标记密码重置token为已使用"""
        pass
    
    @abstractmethod
    async def save_email_verification_token(self, user_id: int, token: str, expires_at) -> None:
        """保存邮箱验证token"""
        pass
        
    @abstractmethod
    async def get_email_verification_token(self, token: str) -> Optional[Dict[str, Any]]:
        """获取邮箱验证token信息"""
        pass
        
    @abstractmethod
    async def mark_email_verification_token_used(self, token: str) -> None:
        """标记邮箱验证token为已使用"""
        pass