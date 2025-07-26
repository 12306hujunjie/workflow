"""用户SQLAlchemy模型"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, Boolean, JSON, BigInteger, Integer, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared_kernel.infrastructure.database.async_session import Base


class UserModel(Base):
    """用户SQLAlchemy模型"""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending_verification", nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 关系
    profile: Mapped[Optional["UserProfileModel"]] = relationship("UserProfileModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions: Mapped[list["UserSessionModel"]] = relationship("UserSessionModel", back_populates="user", cascade="all, delete-orphan")
    login_history: Mapped[list["UserLoginHistoryModel"]] = relationship("UserLoginHistoryModel", back_populates="user", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
        Index("idx_users_status", "status"),
        Index("idx_users_created_at", "created_at"),
    )


class UserProfileModel(Base):
    """用户资料SQLAlchemy模型"""
    
    __tablename__ = "user_profiles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="zh-CN", nullable=False)
    notification_preferences: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="profile")


class UserSessionModel(Base):
    """用户会话SQLAlchemy模型"""
    
    __tablename__ = "user_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    refresh_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    device_info: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # 关系
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="sessions")
    
    # 索引
    __table_args__ = (
        Index("idx_user_sessions_token", "session_token"),
        Index("idx_user_sessions_user_id", "user_id"),
        Index("idx_user_sessions_expires", "expires_at"),
        Index("idx_user_sessions_active", "is_active"),
    )


class UserLoginHistoryModel(Base):
    """用户登录历史SQLAlchemy模型"""
    
    __tablename__ = "user_login_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    login_status: Mapped[str] = mapped_column(String(20), nullable=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location_info: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # 关系
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="login_history")
    
    # 索引
    __table_args__ = (
        Index("idx_login_history_user_id", "user_id"),
        Index("idx_login_history_created_at", "created_at"),
        Index("idx_login_history_ip", "ip_address"),
    )


class PasswordResetTokenModel(Base):
    """密码重置令牌SQLAlchemy模型"""
    
    __tablename__ = "password_reset_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 索引
    __table_args__ = (
        Index("idx_password_reset_token", "token"),
        Index("idx_password_reset_expires", "expires_at"),
        Index("idx_password_reset_used", "is_used"),
    )


class EmailVerificationTokenModel(Base):
    """邮箱验证令牌SQLAlchemy模型"""
    
    __tablename__ = "email_verification_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 索引
    __table_args__ = (
        Index("idx_email_verification_token", "token"),
        Index("idx_email_verification_expires", "expires_at"),
        Index("idx_email_verification_verified", "is_verified"),
    )