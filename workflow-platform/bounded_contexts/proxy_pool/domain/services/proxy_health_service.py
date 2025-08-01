"""Proxy health management domain service."""

from abc import ABC, abstractmethod
from typing import List, Optional
import asyncio
from datetime import datetime, timedelta

from ..entities import Proxy
from ..value_objects import HealthCheckConfig, HealthCheckResult, HealthStatus
from ..exceptions import ProxyHealthCheckError


class IProxyHealthChecker(ABC):
    """代理健康检查器接口"""
    
    @abstractmethod
    async def check_connectivity(
        self, 
        proxy: Proxy, 
        config: HealthCheckConfig
    ) -> HealthCheckResult:
        """检查连接性"""
        pass
    
    @abstractmethod
    async def check_anonymity(
        self, 
        proxy: Proxy, 
        config: HealthCheckConfig
    ) -> HealthCheckResult:
        """检查匿名性"""
        pass
    
    @abstractmethod
    async def check_geo_location(
        self, 
        proxy: Proxy, 
        config: HealthCheckConfig
    ) -> HealthCheckResult:
        """检查地理位置"""
        pass


class ProxyHealthService:
    """代理健康管理领域服务"""
    
    def __init__(self, health_checker: IProxyHealthChecker):
        self._health_checker = health_checker
    
    async def perform_comprehensive_health_check(
        self, 
        proxy: Proxy, 
        config: HealthCheckConfig
    ) -> HealthCheckResult:
        """执行全面健康检查"""
        try:
            # 1. 基础连接性检查
            connectivity_result = await self._health_checker.check_connectivity(proxy, config)
            
            if not connectivity_result.success:
                return connectivity_result
            
            # 2. 匿名性检查（如果启用）
            anonymity_result = None
            if config.anonymity_check:
                try:
                    anonymity_result = await self._health_checker.check_anonymity(proxy, config)
                except Exception as e:
                    # 匿名性检查失败不应该影响整体结果，但要记录
                    pass
            
            # 3. 地理位置验证（如果启用）
            geo_result = None
            if config.geo_verification and proxy.configuration.geo_location:
                try:
                    geo_result = await self._health_checker.check_geo_location(proxy, config)
                except Exception as e:
                    # 地理位置验证失败不应该影响整体结果
                    pass
            
            # 合并结果
            final_result = self._merge_health_check_results(
                connectivity_result, 
                anonymity_result, 
                geo_result
            )
            
            return final_result
            
        except Exception as e:
            return HealthCheckResult(
                timestamp=datetime.utcnow(),
                success=False,
                error_message=f"Health check failed: {str(e)}",
                check_type="comprehensive"
            )
    
    def _merge_health_check_results(
        self,
        connectivity: HealthCheckResult,
        anonymity: Optional[HealthCheckResult] = None,
        geo: Optional[HealthCheckResult] = None
    ) -> HealthCheckResult:
        """合并健康检查结果"""
        # 基础结果以连接性检查为准
        success = connectivity.success
        response_time = connectivity.response_time
        error_message = connectivity.error_message
        
        # 匿名性信息
        anonymity_level = None
        real_ip_detected = None
        
        if anonymity and anonymity.success:
            anonymity_level = anonymity.anonymity_level
            real_ip_detected = anonymity.real_ip_detected
        
        return HealthCheckResult(
            timestamp=datetime.utcnow(),
            success=success,
            response_time=response_time,
            error_message=error_message,
            anonymity_level=anonymity_level,
            real_ip_detected=real_ip_detected,
            check_type="comprehensive"
        )
    
    async def perform_batch_health_check(
        self,
        proxies: List[Proxy],
        config: HealthCheckConfig,
        max_concurrent: int = 10
    ) -> List[tuple[Proxy, HealthCheckResult]]:
        """批量健康检查"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def check_single_proxy(proxy: Proxy) -> tuple[Proxy, HealthCheckResult]:
            async with semaphore:
                result = await self.perform_comprehensive_health_check(proxy, config)
                return proxy, result
        
        # 创建并发任务
        tasks = [check_single_proxy(proxy) for proxy in proxies]
        
        # 执行并收集结果
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # 为异常的代理创建失败结果
                error_result = HealthCheckResult(
                    timestamp=datetime.utcnow(),
                    success=False,
                    error_message=f"Health check exception: {str(result)}",
                    check_type="batch"
                )
                valid_results.append((proxies[i], error_result))
            else:
                valid_results.append(result)
        
        return valid_results
    
    def should_quarantine_proxy(
        self, 
        proxy: Proxy, 
        quarantine_threshold: int = 5
    ) -> bool:
        """判断是否应该隔离代理"""
        # 已经被隔离
        if proxy.is_quarantined:
            return False
        
        # 连续失败次数超过阈值
        if proxy.metrics.consecutive_failures >= quarantine_threshold:
            return True
        
        # 成功率过低且有足够的样本
        if (proxy.metrics.total_requests >= 20 and 
            proxy.metrics.success_rate < 0.1):
            return True
        
        # 响应时间过长
        if (proxy.metrics.average_response_time > 0 and 
            proxy.metrics.average_response_time > 30000):  # 30秒
            return True
        
        return False
    
    def should_recover_proxy(
        self, 
        proxy: Proxy, 
        recovery_success_threshold: int = 3
    ) -> bool:
        """判断隔离的代理是否应该恢复"""
        if not proxy.is_quarantined:
            return False
        
        # 检查最近的健康检查结果
        if proxy.last_health_check and proxy.last_health_check.success:
            # 需要连续成功几次才能恢复
            recent_successes = proxy.metrics.consecutive_successes
            return recent_successes >= recovery_success_threshold
        
        return False
    
    def calculate_next_check_time(
        self, 
        proxy: Proxy, 
        base_interval_minutes: int = 5
    ) -> datetime:
        """计算下次检查时间"""
        now = datetime.utcnow()
        
        # 基于代理健康状态调整检查间隔
        if proxy.health_status == HealthStatus.HEALTHY:
            # 健康代理检查间隔较长
            interval = base_interval_minutes * 2
        elif proxy.health_status == HealthStatus.DEGRADED:
            # 降级代理正常间隔
            interval = base_interval_minutes
        elif proxy.health_status == HealthStatus.UNHEALTHY:
            # 不健康代理检查更频繁
            interval = base_interval_minutes // 2
        elif proxy.health_status == HealthStatus.QUARANTINED:
            # 隔离代理检查间隔最长
            interval = base_interval_minutes * 4
        else:
            # 未知状态，使用默认间隔
            interval = base_interval_minutes
        
        # 基于历史表现进一步调整
        if proxy.metrics.total_requests > 0:
            # 成功率高的代理可以降低检查频率
            success_rate = proxy.metrics.success_rate
            if success_rate > 0.95:
                interval = int(interval * 1.5)
            elif success_rate < 0.5:
                interval = max(1, int(interval * 0.5))
        
        return now + timedelta(minutes=interval)
    
    def get_health_summary(self, proxies: List[Proxy]) -> dict:
        """获取健康状态摘要"""
        if not proxies:
            return {
                'total_proxies': 0,
                'healthy': 0,
                'degraded': 0,
                'unhealthy': 0,
                'quarantined': 0,
                'unknown': 0,
                'health_distribution': {},
                'average_response_time': 0.0,
                'overall_success_rate': 0.0
            }
        
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.QUARANTINED: 0,
            HealthStatus.UNKNOWN: 0
        }
        
        total_response_time = 0.0
        response_time_count = 0
        total_requests = 0
        total_successful = 0
        
        for proxy in proxies:
            # 统计状态分布
            status_counts[proxy.health_status] += 1
            
            # 统计响应时间
            if proxy.metrics.average_response_time > 0:
                total_response_time += proxy.metrics.average_response_time
                response_time_count += 1
            
            # 统计成功率
            total_requests += proxy.metrics.total_requests
            total_successful += proxy.metrics.successful_requests
        
        avg_response_time = (total_response_time / response_time_count 
                           if response_time_count > 0 else 0.0)
        
        overall_success_rate = (total_successful / total_requests 
                              if total_requests > 0 else 0.0)
        
        return {
            'total_proxies': len(proxies),
            'healthy': status_counts[HealthStatus.HEALTHY],
            'degraded': status_counts[HealthStatus.DEGRADED],
            'unhealthy': status_counts[HealthStatus.UNHEALTHY],
            'quarantined': status_counts[HealthStatus.QUARANTINED],
            'unknown': status_counts[HealthStatus.UNKNOWN],
            'health_distribution': {
                status.value: count for status, count in status_counts.items()
            },
            'average_response_time': avg_response_time,
            'overall_success_rate': overall_success_rate
        }
    
    def prioritize_proxies_for_health_check(
        self, 
        proxies: List[Proxy],
        max_count: int = 100
    ) -> List[Proxy]:
        """优先排序需要健康检查的代理"""
        if not proxies:
            return []
        
        # 按优先级排序
        def priority_score(proxy: Proxy) -> tuple:
            # 返回元组用于排序，数值越小优先级越高
            
            # 1. 从未检查过的代理优先级最高
            if proxy.last_health_check is None:
                return (0, 0, 0)
            
            # 2. 不健康的代理优先级较高
            health_priority = {
                HealthStatus.UNHEALTHY: 1,
                HealthStatus.DEGRADED: 2, 
                HealthStatus.QUARANTINED: 3,
                HealthStatus.HEALTHY: 4,
                HealthStatus.UNKNOWN: 5
            }.get(proxy.health_status, 6)
            
            # 3. 检查时间越久的优先级越高
            last_check_age = (datetime.utcnow() - 
                            (proxy.last_health_check.timestamp if proxy.last_health_check else datetime.min)
                            ).total_seconds()
            
            # 4. 使用频率高的代理优先级较高
            usage_priority = -proxy.metrics.total_requests  # 负数表示使用越多优先级越高
            
            return (health_priority, -last_check_age, usage_priority)
        
        # 排序并返回前N个
        sorted_proxies = sorted(proxies, key=priority_score)
        return sorted_proxies[:max_count]