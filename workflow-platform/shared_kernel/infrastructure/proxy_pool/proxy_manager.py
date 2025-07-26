from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import aiohttp
from abc import ABC, abstractmethod


class ProxyStatus(Enum):
    """代理状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    FAILED = "failed"


class ProxyType(Enum):
    """代理类型枚举"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


@dataclass
class ProxyInfo:
    """代理信息"""
    id: str
    host: str
    port: int
    proxy_type: ProxyType
    username: Optional[str] = None
    password: Optional[str] = None
    status: ProxyStatus = ProxyStatus.INACTIVE
    last_used: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    response_time: Optional[float] = None  # 响应时间（毫秒）
    success_rate: float = 0.0  # 成功率
    total_requests: int = 0
    failed_requests: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @property
    def url(self) -> str:
        """获取代理URL"""
        if self.username and self.password:
            return f"{self.proxy_type.value}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.proxy_type.value}://{self.host}:{self.port}"
    
    def update_stats(self, success: bool, response_time: Optional[float] = None):
        """更新统计信息"""
        self.total_requests += 1
        if not success:
            self.failed_requests += 1
        
        self.success_rate = (self.total_requests - self.failed_requests) / self.total_requests
        
        if response_time is not None:
            self.response_time = response_time
        
        self.last_used = datetime.utcnow()


class ProxyRepository(ABC):
    """代理仓储接口"""
    
    @abstractmethod
    async def save(self, proxy: ProxyInfo) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, proxy_id: str) -> Optional[ProxyInfo]:
        pass
    
    @abstractmethod
    async def find_active_proxies(self, limit: int = 10) -> List[ProxyInfo]:
        pass
    
    @abstractmethod
    async def find_all(self) -> List[ProxyInfo]:
        pass
    
    @abstractmethod
    async def delete(self, proxy_id: str) -> None:
        pass


class ProxyTester:
    """代理测试器"""
    
    def __init__(self, test_url: str = "http://httpbin.org/ip", timeout: int = 10):
        self.test_url = test_url
        self.timeout = timeout
    
    async def test_proxy(self, proxy: ProxyInfo) -> bool:
        """测试代理是否可用"""
        try:
            start_time = datetime.utcnow()
            
            connector = aiohttp.TCPConnector()
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            ) as session:
                async with session.get(
                    self.test_url,
                    proxy=proxy.url
                ) as response:
                    if response.status == 200:
                        end_time = datetime.utcnow()
                        response_time = (end_time - start_time).total_seconds() * 1000
                        proxy.response_time = response_time
                        proxy.status = ProxyStatus.ACTIVE
                        proxy.last_checked = datetime.utcnow()
                        return True
                    else:
                        proxy.status = ProxyStatus.FAILED
                        return False
        
        except Exception as e:
            proxy.status = ProxyStatus.FAILED
            proxy.last_checked = datetime.utcnow()
            return False


class ProxyManager:
    """代理管理器"""
    
    def __init__(self, repository: ProxyRepository, tester: ProxyTester):
        self.repository = repository
        self.tester = tester
        self._current_proxy_index = 0
    
    async def add_proxy(self, host: str, port: int, proxy_type: ProxyType,
                       username: Optional[str] = None, password: Optional[str] = None) -> ProxyInfo:
        """添加代理"""
        proxy_id = f"{host}:{port}"
        proxy = ProxyInfo(
            id=proxy_id,
            host=host,
            port=port,
            proxy_type=proxy_type,
            username=username,
            password=password
        )
        
        # 测试代理
        await self.tester.test_proxy(proxy)
        
        # 保存代理
        await self.repository.save(proxy)
        
        return proxy
    
    async def get_available_proxy(self) -> Optional[ProxyInfo]:
        """获取可用的代理（轮询方式）"""
        active_proxies = await self.repository.find_active_proxies()
        
        if not active_proxies:
            return None
        
        # 轮询选择代理
        proxy = active_proxies[self._current_proxy_index % len(active_proxies)]
        self._current_proxy_index += 1
        
        return proxy
    
    async def get_best_proxy(self) -> Optional[ProxyInfo]:
        """获取最佳代理（基于成功率和响应时间）"""
        active_proxies = await self.repository.find_active_proxies()
        
        if not active_proxies:
            return None
        
        # 根据成功率和响应时间排序
        def score_proxy(proxy: ProxyInfo) -> float:
            success_weight = 0.7
            speed_weight = 0.3
            
            success_score = proxy.success_rate
            # 响应时间越小越好，转换为分数（最大1000ms）
            speed_score = max(0, 1 - (proxy.response_time or 1000) / 1000) if proxy.response_time else 0
            
            return success_weight * success_score + speed_weight * speed_score
        
        best_proxy = max(active_proxies, key=score_proxy)
        return best_proxy
    
    async def update_proxy_stats(self, proxy_id: str, success: bool, response_time: Optional[float] = None):
        """更新代理统计信息"""
        proxy = await self.repository.find_by_id(proxy_id)
        if proxy:
            proxy.update_stats(success, response_time)
            await self.repository.save(proxy)
    
    async def test_all_proxies(self):
        """测试所有代理"""
        all_proxies = await self.repository.find_all()
        
        tasks = []
        for proxy in all_proxies:
            task = asyncio.create_task(self.tester.test_proxy(proxy))
            tasks.append((proxy, task))
        
        for proxy, task in tasks:
            try:
                await task
                await self.repository.save(proxy)
            except Exception as e:
                proxy.status = ProxyStatus.FAILED
                await self.repository.save(proxy)
    
    async def remove_failed_proxies(self, max_failed_rate: float = 0.8):
        """移除失败率过高的代理"""
        all_proxies = await self.repository.find_all()
        
        for proxy in all_proxies:
            if proxy.total_requests > 10 and (1 - proxy.success_rate) > max_failed_rate:
                await self.repository.delete(proxy.id)
    
    async def get_proxy_stats(self) -> Dict[str, Any]:
        """获取代理池统计信息"""
        all_proxies = await self.repository.find_all()
        active_proxies = [p for p in all_proxies if p.status == ProxyStatus.ACTIVE]
        
        total_requests = sum(p.total_requests for p in all_proxies)
        total_failed = sum(p.failed_requests for p in all_proxies)
        
        return {
            "total_proxies": len(all_proxies),
            "active_proxies": len(active_proxies),
            "inactive_proxies": len(all_proxies) - len(active_proxies),
            "total_requests": total_requests,
            "total_failed_requests": total_failed,
            "overall_success_rate": (total_requests - total_failed) / total_requests if total_requests > 0 else 0,
            "average_response_time": sum(p.response_time or 0 for p in active_proxies) / len(active_proxies) if active_proxies else 0
        }