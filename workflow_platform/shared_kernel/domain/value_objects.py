"""共享值对象"""

import re
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class Email(BaseModel):
    """邮箱值对象"""
    value: str = Field(..., min_length=3, max_length=255)
    
    @validator('value')
    def validate_email_format(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v
    
    def __str__(self) -> str:
        return self.value
    
    class Config:
        frozen = True


class Username(BaseModel):
    """用户名值对象"""
    value: str = Field(..., min_length=3, max_length=50)
    
    @validator('value')
    def validate_username_format(cls, v):
        # 只允许字母、数字、下划线
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers and underscores')
        return v
    
    def __str__(self) -> str:
        return self.value
    
    class Config:
        frozen = True


class HashedPassword(BaseModel):
    """哈希密码值对象"""
    value: str = Field(..., min_length=1)
    
    def __str__(self) -> str:
        return self.value
    
    class Config:
        frozen = True


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"