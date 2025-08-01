"""用户API schemas"""

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, EmailStr, field_validator


def validate_password_strength(v: str) -> str:
    """验证密码强度"""
    if len(v) < 8:
        raise ValueError("密码长度至少需要8个字符")
    has_upper = any(c.isupper() for c in v)
    has_lower = any(c.islower() for c in v)
    has_digit = any(c.isdigit() for c in v)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
    if not has_upper:
        raise ValueError("密码需要包含至少一个大写字母")
    if not has_lower:
        raise ValueError("密码需要包含至少一个小写字母")
    if not has_digit:
        raise ValueError("密码需要包含至少一个数字")
    if not has_special:
        raise ValueError("密码需要包含至少一个特殊字符")
    return v


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, description="密码")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username_or_email: str = Field(..., min_length=3, description="用户名或邮箱")
    password: str = Field(..., min_length=1, description="密码")


class UpdateProfileRequest(BaseModel):
    """更新用户资料请求"""
    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    timezone: Optional[str] = Field(None, max_length=50, description="时区")
    language: Optional[str] = Field(None, max_length=10, description="语言")
    notification_preferences: Optional[Dict[str, Any]] = Field(None, description="通知偏好")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=1, description="原密码")
    new_password: str = Field(..., min_length=8, description="新密码")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        return validate_password_strength(v)


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    email: EmailStr = Field(..., description="注册邮箱")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, description="新密码")

class ResetPasswordWithCodeRequest(BaseModel):
    """使用验证码重置密码请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    code: str = Field(..., description="6位验证码", min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, description="新密码")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        return validate_password_strength(v)

class ResendVerificationCodeRequest(BaseModel):
    """重新发送验证码请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    purpose: str = Field(..., description="验证码用途", pattern="^(register|reset_password)$")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")


class EmailVerificationRequest(BaseModel):
    """邮箱验证请求"""
    token: str = Field(..., description="验证令牌")

class EmailVerificationCodeRequest(BaseModel):
    """邮箱验证码验证请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    code: str = Field(..., description="6位验证码", min_length=6, max_length=6)


class LogoutRequest(BaseModel):
    """登出请求"""
    refresh_token: Optional[str] = Field(None, description="刷新令牌（可选）")


class RegisterUserRequest(BaseModel):
    """用户注册请求（包含验证码）"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, description="密码")
    code: str = Field(..., description="6位验证码", min_length=6, max_length=6)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)


class UserProfileResponse(BaseModel):
    """用户资料响应"""
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    timezone: str = "UTC"
    language: str = "zh-CN"
    notification_preferences: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    status: str
    role: str
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    profile: Optional[UserProfileResponse] = None

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class UserListResponse(BaseModel):
    """用户列表响应"""
    items: list[UserResponse]
    total: int
    page: int = 1
    per_page: int = 20
    total_pages: int = 1


class LoginResponse(BaseModel):
    """登录响应"""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """消息响应"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    success: bool = False
