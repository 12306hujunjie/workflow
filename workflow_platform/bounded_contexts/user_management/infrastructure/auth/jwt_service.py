"""JWT认证服务"""

import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
import secrets
from shared_kernel.infrastructure.redis_service import RedisService


class JWTService:
    """JWT认证服务"""
    
    def __init__(
        self, 
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
        redis_service: Optional[RedisService] = None
    ):
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.redis_service = redis_service
    
    def create_access_token(self, user_id: int, username: str, role: str) -> str:
        """创建访问令牌"""
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes),
            "iat": datetime.now(timezone.utc),
            "nbf": datetime.now(timezone.utc),
            "jti": secrets.token_urlsafe(16)  # JWT ID for blacklisting
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
    
    async def verify_access_token(self, token: str) -> Dict[str, Any]:
        """验证访问令牌"""
        payload = self.decode_token(token)
        
        if payload.get("type") != "access":
            raise ValueError("令牌类型错误")
        
        # 检查token是否在黑名单中
        if await self.is_token_blacklisted(token):
            raise ValueError("令牌已被撤销")
        
        # 检查用户的所有token是否被撤销
        user_id = payload.get("user_id")
        token_issued_at = datetime.fromtimestamp(payload.get("iat"), tz=timezone.utc)
        if await self.is_user_tokens_blacklisted(user_id, token_issued_at):
            raise ValueError("用户令牌已被全部撤销")
        
        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("role"),
            "jti": payload.get("jti")
        }
    
    async def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """验证刷新令牌"""
        payload = self.decode_token(token)
        
        if payload.get("type") != "refresh":
            raise ValueError("令牌类型错误")
        
        # 检查token是否在黑名单中
        if await self.is_token_blacklisted(token):
            raise ValueError("令牌已被撤销")
        
        # 检查用户的所有token是否被撤销
        user_id = payload.get("user_id")
        token_issued_at = datetime.fromtimestamp(payload.get("iat"), tz=timezone.utc)
        if await self.is_user_tokens_blacklisted(user_id, token_issued_at):
            raise ValueError("用户令牌已被全部撤销")
        
        return {
            "user_id": payload.get("user_id"),
            "jti": payload.get("jti")
        }
    
    async def refresh_access_token(self, refresh_token: str, username: str, role: str) -> str:
        """使用刷新令牌创建新的访问令牌"""
        payload = await self.verify_refresh_token(refresh_token)
        return self.create_access_token(payload["user_id"], username, role)
    
    def get_token_expires_at(self, token: str) -> datetime:
        """获取令牌过期时间"""
        payload = self.decode_token(token)
        exp_timestamp = payload.get("exp")
        return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    
    async def blacklist_token(self, token: str) -> bool:
        """将token加入黑名单"""
        if not self.redis_service:
            # 如果没有Redis服务，返回True表示操作成功（但实际上没有黑名单功能）
            return True
        
        try:
            payload = self.decode_token(token)
            jti = payload.get("jti")
            if not jti:
                return False
            
            # 计算token剩余有效时间
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                expires_at = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
                now = datetime.now(timezone.utc)
                if expires_at > now:
                    ttl = int((expires_at - now).total_seconds())
                    # 将token的jti加入黑名单，设置过期时间为token的剩余有效时间
                    blacklist_key = f"blacklist:token:{jti}"
                    return await self.redis_service.set(blacklist_key, "1", expire=ttl)
            return False
        except Exception:
            return False
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """检查token是否在黑名单中"""
        if not self.redis_service:
            # 如果没有Redis服务，返回False表示不在黑名单中
            return False
        
        try:
            payload = self.decode_token(token)
            jti = payload.get("jti")
            if not jti:
                return False
            
            blacklist_key = f"blacklist:token:{jti}"
            return await self.redis_service.exists(blacklist_key)
        except Exception:
            return False
    
    async def blacklist_user_tokens(self, user_id: int) -> bool:
        """将用户的所有token加入黑名单"""
        if not self.redis_service:
            return True
        
        try:
            # 设置用户token黑名单标记，有效期为最长的refresh token有效期
            blacklist_key = f"blacklist:user:{user_id}"
            ttl = self.refresh_token_expire_days * 24 * 3600  # 转换为秒
            return await self.redis_service.set(blacklist_key, str(datetime.now(timezone.utc).timestamp()), expire=ttl)
        except Exception:
            return False
    
    async def is_user_tokens_blacklisted(self, user_id: int, token_issued_at: datetime) -> bool:
        """检查用户token是否在黑名单中（基于签发时间）"""
        if not self.redis_service:
            return False
        
        try:
            blacklist_key = f"blacklist:user:{user_id}"
            blacklist_timestamp_str = await self.redis_service.get(blacklist_key)
            if blacklist_timestamp_str:
                blacklist_timestamp = float(blacklist_timestamp_str)
                blacklist_time = datetime.fromtimestamp(blacklist_timestamp, tz=timezone.utc)
                # 如果token的签发时间早于黑名单时间，则认为token已被撤销
                return token_issued_at < blacklist_time
            return False
        except Exception:
            return False