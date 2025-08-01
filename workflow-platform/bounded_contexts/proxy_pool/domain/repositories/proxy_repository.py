"""Proxy repository interface - Domain layer contract."""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities import ProxyId, Proxy
from ..value_objects import ProxyFilters, HealthStatus


class IProxyRepository(ABC):
    """代理仓储接口"""
    
    @abstractmethod
    async def save(self, proxy: Proxy) -> None:
        """保存代理"""
        pass
    
    @abstractmethod
    async def find_by_id(self, proxy_id: ProxyId) -> Optional[Proxy]:
        """根据ID查找代理"""
        pass
    
    @abstractmethod
    async def find_by_endpoint(self, host: str, port: int, protocol: str) -> Optional[Proxy]:
        """根据端点查找代理"""
        pass
    
    @abstractmethod
    async def find_available_proxies(
        self, 
        filters: Optional[ProxyFilters] = None,
        limit: int = 50
    ) -> List[Proxy]:
        """查找可用代理"""
        pass
    
    @abstractmethod
    async def find_by_health_status(
        self, 
        status: HealthStatus,
        limit: Optional[int] = None
    ) -> List[Proxy]:
        """根据健康状态查找代理"""
        pass
    
    @abstractmethod
    async def find_by_country(self, country_code: str, limit: int = 50) -> List[Proxy]:
        """根据国家查找代理"""
        pass
    
    @abstractmethod
    async def find_all(self, limit: Optional[int] = None) -> List[Proxy]:
        """查找所有代理"""
        pass
    
    @abstractmethod
    async def count_total(self) -> int:
        """获取代理总数"""
        pass
    
    @abstractmethod
    async def count_by_status(self, status: HealthStatus) -> int:
        """根据状态获取代理数量"""
        pass
    
    @abstractmethod
    async def delete(self, proxy_id: ProxyId) -> bool:
        """删除代理"""
        pass
    
    @abstractmethod
    async def delete_by_criteria(
        self, 
        health_status: Optional[HealthStatus] = None,
        inactive_since: Optional[datetime] = None,
        success_rate_below: Optional[float] = None
    ) -> int:
        """根据条件批量删除代理"""
        pass
    
    @abstractmethod
    async def exists(self, proxy_id: ProxyId) -> bool:
        """检查代理是否存在"""
        pass
    
    @abstractmethod
    async def find_needing_health_check(
        self, 
        check_interval_minutes: int = 5,
        limit: int = 100
    ) -> List[Proxy]:
        """找到需要健康检查的代理"""
        pass
    
    @abstractmethod
    async def find_quarantined_for_recovery(
        self, 
        recovery_interval_minutes: int = 30,
        limit: int = 50
    ) -> List[Proxy]:
        """找到需要恢复检查的隔离代理"""
        pass
    
    @abstractmethod
    async def update_concurrent_usage(
        self, 
        proxy_id: ProxyId, 
        increment: int
    ) -> None:
        """更新并发使用计数"""
        pass