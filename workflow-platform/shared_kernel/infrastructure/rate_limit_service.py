"""频率限制服务"""

import hashlib
from typing import Optional
from datetime import datetime, timedelta

from .redis_service import RedisService


class RateLimitService:
    """频率限制服务"""
    
    def __init__(self, redis_service: RedisService):
        self.redis = redis_service
    
    def _generate_key(self, ip: str, email: str, endpoint: str) -> str:
        """生成频率限制的Redis键"""
        # 使用IP+邮件+接口名生成唯一标识
        identifier = f"{ip}:{email}:{endpoint}"
        # 使用MD5哈希避免键名过长
        hash_key = hashlib.md5(identifier.encode()).hexdigest()
        return f"rate_limit:{hash_key}"
    
    async def check_rate_limit(
        self, 
        ip: str, 
        email: str, 
        endpoint: str, 
        limit_seconds: int = 180  # 默认3分钟
    ) -> tuple[bool, Optional[int]]:
        """
        检查频率限制
        
        Args:
            ip: 客户端IP
            email: 邮箱地址
            endpoint: 接口名称
            limit_seconds: 限制时间（秒）
            
        Returns:
            (is_allowed, remaining_seconds)
            is_allowed: 是否允许访问
            remaining_seconds: 剩余等待时间（如果被限制）
        """
        key = self._generate_key(ip, email, endpoint)
        
        # 检查是否存在限制记录
        last_request_time = await self.redis.get(key)
        
        if last_request_time is None:
            # 没有记录，允许访问
            return True, None
        
        # 计算时间差
        last_time = datetime.fromisoformat(last_request_time)
        now = datetime.now()
        elapsed = (now - last_time).total_seconds()
        
        if elapsed >= limit_seconds:
            # 超过限制时间，允许访问
            return True, None
        else:
            # 还在限制时间内，拒绝访问
            remaining = int(limit_seconds - elapsed)
            return False, remaining
    
    async def record_request(
        self, 
        ip: str, 
        email: str, 
        endpoint: str, 
        limit_seconds: int = 180
    ) -> None:
        """
        记录请求时间
        
        Args:
            ip: 客户端IP
            email: 邮箱地址
            endpoint: 接口名称
            limit_seconds: 限制时间（秒）
        """
        key = self._generate_key(ip, email, endpoint)
        now = datetime.now().isoformat()
        
        # 设置记录，并设置过期时间
        await self.redis.set(key, now, expire=limit_seconds)
    
    async def is_rate_limited(
        self, 
        ip: str, 
        email: str, 
        endpoint: str, 
        limit_seconds: int = 180
    ) -> tuple[bool, Optional[int]]:
        """
        检查是否被频率限制（便捷方法）
        
        Returns:
            (is_limited, remaining_seconds)
        """
        is_allowed, remaining = await self.check_rate_limit(
            ip, email, endpoint, limit_seconds
        )
        return not is_allowed, remaining
    
    async def apply_rate_limit(
        self, 
        ip: str, 
        email: str, 
        endpoint: str, 
        limit_seconds: int = 180
    ) -> None:
        """
        应用频率限制（检查并记录）
        
        Raises:
            ValueError: 如果触发频率限制
        """
        is_limited, remaining = await self.is_rate_limited(
            ip, email, endpoint, limit_seconds
        )
        
        if is_limited:
            minutes = remaining // 60
            seconds = remaining % 60
            if minutes > 0:
                raise ValueError(f"请求过于频繁，请等待 {minutes} 分 {seconds} 秒后再试")
            else:
                raise ValueError(f"请求过于频繁，请等待 {seconds} 秒后再试")
        
        # 记录这次请求
        await self.record_request(ip, email, endpoint, limit_seconds)
    
    async def clear_rate_limit(
        self, 
        ip: str, 
        email: str, 
        endpoint: str
    ) -> None:
        """清除频率限制记录（用于测试或管理）"""
        key = self._generate_key(ip, email, endpoint)
        await self.redis.delete(key)
    
    async def get_remaining_time(
        self, 
        ip: str, 
        email: str, 
        endpoint: str
    ) -> Optional[int]:
        """获取剩余等待时间"""
        _, remaining = await self.is_rate_limited(ip, email, endpoint)
        return remaining