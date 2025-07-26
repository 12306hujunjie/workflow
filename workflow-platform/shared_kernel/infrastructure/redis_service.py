"""Redis服务"""

import redis.asyncio as redis
from typing import Optional, Union
from datetime import timedelta
import json


class RedisService:
    """Redis服务类"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None
    
    async def get_client(self) -> redis.Redis:
        """获取Redis客户端"""
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client
    
    async def close(self):
        """关闭Redis连接"""
        if self._client:
            await self._client.close()
            self._client = None
    
    async def set(
        self, 
        key: str, 
        value: Union[str, dict, list], 
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """设置键值对"""
        client = await self.get_client()
        
        # 如果值是字典或列表，转换为JSON字符串
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        if expire:
            if isinstance(expire, timedelta):
                expire = int(expire.total_seconds())
            return await client.setex(key, expire, value)
        else:
            return await client.set(key, value)
    
    async def get(self, key: str) -> Optional[str]:
        """获取值"""
        client = await self.get_client()
        return await client.get(key)
    
    async def get_json(self, key: str) -> Optional[Union[dict, list]]:
        """获取JSON值"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def delete(self, *keys: str) -> int:
        """删除键"""
        client = await self.get_client()
        return await client.delete(*keys)
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        client = await self.get_client()
        return bool(await client.exists(key))
    
    async def expire(self, key: str, seconds: Union[int, timedelta]) -> bool:
        """设置键的过期时间"""
        client = await self.get_client()
        if isinstance(seconds, timedelta):
            seconds = int(seconds.total_seconds())
        return await client.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        """获取键的剩余生存时间"""
        client = await self.get_client()
        return await client.ttl(key)
    
    async def sadd(self, key: str, *values: str) -> int:
        """向集合添加元素"""
        client = await self.get_client()
        return await client.sadd(key, *values)
    
    async def srem(self, key: str, *values: str) -> int:
        """从集合删除元素"""
        client = await self.get_client()
        return await client.srem(key, *values)
    
    async def sismember(self, key: str, value: str) -> bool:
        """检查元素是否在集合中"""
        client = await self.get_client()
        return await client.sismember(key, value)
    
    async def smembers(self, key: str) -> set:
        """获取集合所有成员"""
        client = await self.get_client()
        return await client.smembers(key)
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        client = await self.get_client()
        return await client.incr(key, amount)
    
    async def decr(self, key: str, amount: int = 1) -> int:
        """递减计数器"""
        client = await self.get_client()
        return await client.decr(key, amount)
    
    async def ping(self) -> bool:
        """测试Redis连接"""
        try:
            client = await self.get_client()
            response = await client.ping()
            return response is True
        except Exception:
            return False