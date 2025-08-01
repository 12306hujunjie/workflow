"""用户相关命令"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator


class RegisterUserCommand(BaseModel):
    """注册用户命令"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('username')
    def validate_username(cls, v):
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        return v


class LoginUserCommand(BaseModel):
    """用户登录命令"""
    username_or_email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    @validator('username_or_email')
    def validate_username_or_email(cls, v):
        return v


class UpdateUserProfileCommand(BaseModel):
    """更新用户资料命令"""
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    notification_preferences: Optional[Dict[str, Any]] = None


class ChangePasswordCommand(BaseModel):
    """修改密码命令"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def passwords_different(cls, v, values):
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('新密码不能与旧密码相同')
        return v


class ResetPasswordCommand(BaseModel):
    """重置密码命令"""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


class ForgotPasswordCommand(BaseModel):
    """忘记密码命令"""
    email: EmailStr
    
    @validator('email')
    def validate_email(cls, v):
        return v


class VerifyEmailCommand(BaseModel):
    """验证邮箱命令"""
    token: str = Field(..., min_length=1)


class ResendVerificationEmailCommand(BaseModel):
    """重新发送验证邮件命令"""
    email: EmailStr
    
    @validator('email')
    def validate_email(cls, v):
        return v