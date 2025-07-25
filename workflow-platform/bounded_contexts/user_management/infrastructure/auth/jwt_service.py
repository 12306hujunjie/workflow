"""JWT认证服务"""

import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
import secrets


class JWTService:
    """JWT认证服务"""
    
    def __init__(
        self, 
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    def create_access_token(self, user_id: int, username: str, role: str) -> str:
        """创建访问令牌"""
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes),
            "iat": datetime.now(timezone.utc),
            "nbf": datetime.now(timezone.utc)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: int) -> str:
        """创建刷新令牌"""
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days),
            "iat": datetime.now(timezone.utc),
            "nbf": datetime.now(timezone.utc),
            "jti": secrets.token_urlsafe(16)  # JWT ID for blacklisting
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_token_pair(self, user_id: int, username: str, role: str) -> Tuple[str, str]:
        """创建访问令牌和刷新令牌对"""
        access_token = self.create_access_token(user_id, username, role)
        refresh_token = self.create_refresh_token(user_id)
        return access_token, refresh_token
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """解码令牌"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": True, "verify_nbf": True}
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("令牌已过期")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"无效的令牌: {str(e)}")
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """验证访问令牌"""
        payload = self.decode_token(token)
        
        if payload.get("type") != "access":
            raise ValueError("令牌类型错误")
        
        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """验证刷新令牌"""
        payload = self.decode_token(token)
        
        if payload.get("type") != "refresh":
            raise ValueError("令牌类型错误")
        
        return {
            "user_id": payload.get("user_id"),
            "jti": payload.get("jti")
        }
    
    def refresh_access_token(self, refresh_token: str, username: str, role: str) -> str:
        """使用刷新令牌创建新的访问令牌"""
        payload = self.verify_refresh_token(refresh_token)
        return self.create_access_token(payload["user_id"], username, role)
    
    def get_token_expires_at(self, token: str) -> datetime:
        """获取令牌过期时间"""
        payload = self.decode_token(token)
        exp_timestamp = payload.get("exp")
        return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)