"""Proxy pool application service - Orchestrates domain services and use cases."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio

from ...domain.entities import ProxyId, Proxy
from ...domain.repositories import IProxyRepository
from ...domain.services import ProxySelectionService, ProxyHealthService
from ...domain.value_objects import (
    ProxyConfiguration,
    SelectionStrategy,
    SelectionContext,
    ProxyFilters,
    HealthCheckConfig,
    HealthStatus
)
from ...domain.exceptions import (
    NoAvailableProxyError,
    ProxyNotFoundError,
    ProxySelectionError,
    ProxyPoolApplicationError
)
from shared_kernel.infrastructure.event_publisher import IEventPublisher


class GetProxyRequest:
    """获取代理请求"""
    
    def __init__(
        self,
        filters: Optional[ProxyFilters] = None,
        selection_strategy: Optional[SelectionStrategy] = None,
        context: Optional[SelectionContext] = None
    ):
        self.filters = filters or ProxyFilters()
        self.selection_strategy = selection_strategy or SelectionStrategy.best_strategy()
        self.context = context or SelectionContext()


class GetProxyResponse:
    """获取代理响应"""
    
    def __init__(self, proxy: Proxy):
        self.proxy = proxy
        self.proxy_id = str(proxy.id)
        self.url = proxy.configuration.url
        self.host = proxy.configuration.endpoint.host
        self.port = proxy.configuration.endpoint.port
        self.protocol = proxy.configuration.endpoint.protocol.value
        self.health_status = proxy.health_status.value
        self.selection_score = 0.0  # Will be set by selection service


class AddProxyRequest:
    """添加代理请求"""
    
    def __init__(self, configuration: ProxyConfiguration):
        self.configuration = configuration


class ReportResultRequest:
    """报告结果请求"""
    
    def __init__(
        self,
        proxy_id: str,
        success: bool,
        response_time: Optional[float] = None,
        http_status: Optional[int] = None,
        error_message: Optional[str] = None,
        target_host: Optional[str] = None
    ):
        self.proxy_id = ProxyId(proxy_id)
        self.success = success
        self.response_time = response_time
        self.http_status = http_status
        self.error_message = error_message
        self.target_host = target_host


class HealthCheckRequest:
    """健康检查请求"""
    
    def __init__(
        self,
        proxy_id: Optional[str] = None,
        config: Optional[HealthCheckConfig] = None,
        force: bool = False
    ):
        self.proxy_id = ProxyId(proxy_id) if proxy_id else None
        self.config = config or HealthCheckConfig()
        self.force = force


class ProxyPoolApplicationService:
    """代理池应用服务 - 协调各种用例"""
    
    def __init__(
        self,
        proxy_repository: IProxyRepository,
        selection_service: ProxySelectionService,
        health_service: ProxyHealthService,
        event_publisher: Optional[IEventPublisher] = None
    ):
        self._proxy_repository = proxy_repository
        self._selection_service = selection_service
        self._health_service = health_service
        self._event_publisher = event_publisher
    
    async def get_available_proxy(self, request: GetProxyRequest) -> GetProxyResponse:
        """获取可用代理 - 核心用例"""
        try:
            # 1. 从仓储获取符合条件的代理
            available_proxies = await self._proxy_repository.find_available_proxies(
                filters=request.filters,
                limit=100  # 获取足够多的候选代理
            )
            
            if not available_proxies:
                raise NoAvailableProxyError(
                    "No proxies match the specified criteria"
                )
            
            # 2. 使用选择服务选择最优代理
            selected_proxy = self._selection_service.select_optimal_proxy(
                available_proxies=available_proxies,
                strategy=request.selection_strategy,
                context=request.context
            )
            
            if not selected_proxy:
                raise ProxySelectionError(
                    "Failed to select proxy from available candidates"
                )
            
            # 3. 获取代理用于请求
            selected_proxy.acquire_for_request(request.context)
            
            # 4. 保存代理状态更新
            await self._proxy_repository.save(selected_proxy)
            
            # 5. 发布领域事件
            if self._event_publisher:
                domain_events = selected_proxy.domain_events
                for event in domain_events:
                    await self._event_publisher.publish(event)
                selected_proxy.clear_domain_events()
            
            # 6. 创建响应
            response = GetProxyResponse(selected_proxy)
            response.selection_score = selected_proxy.calculate_selection_score(
                request.selection_strategy, request.context
            )
            
            return response
            
        except (NoAvailableProxyError, ProxySelectionError):
            raise
        except Exception as e:
            raise ProxyPoolApplicationError(
                f"Failed to get available proxy: {str(e)}"
            ) from e
    
    async def add_proxy(self, request: AddProxyRequest) -> ProxyId:
        """添加新代理"""
        try:
            # 1. 检查代理是否已存在
            existing_proxy = await self._proxy_repository.find_by_endpoint(
                host=request.configuration.endpoint.host,
                port=request.configuration.endpoint.port,
                protocol=request.configuration.endpoint.protocol.value
            )
            
            if existing_proxy:
                raise ProxyPoolApplicationError(
                    f"Proxy already exists: {request.configuration.endpoint.url}"
                )
            
            # 2. 创建新代理
            proxy_id = ProxyId.from_endpoint(
                host=request.configuration.endpoint.host,
                port=request.configuration.endpoint.port,
                protocol=request.configuration.endpoint.protocol.value
            )
            
            proxy = Proxy(proxy_id, request.configuration)
            
            # 3. 保存代理
            await self._proxy_repository.save(proxy)
            
            # 4. 发布创建事件
            if self._event_publisher:
                domain_events = proxy.domain_events
                for event in domain_events:
                    await self._event_publisher.publish(event)
                proxy.clear_domain_events()
            
            return proxy_id
            
        except Exception as e:
            if isinstance(e, ProxyPoolApplicationError):
                raise
            raise ProxyPoolApplicationError(
                f"Failed to add proxy: {str(e)}"
            ) from e
    
    async def report_proxy_result(self, request: ReportResultRequest) -> None:
        """报告代理使用结果"""
        try:
            # 1. 获取代理
            proxy = await self._proxy_repository.find_by_id(request.proxy_id)
            if not proxy:
                # 忽略不存在的代理，避免影响业务流程
                return
            
            # 2. 记录请求结果
            proxy.record_request_result(
                success=request.success,
                response_time=request.response_time,
                http_status=request.http_status,
                error_message=request.error_message,
                target_host=request.target_host
            )
            
            # 3. 释放代理请求
            proxy.release_from_request()
            
            # 4. 检查是否需要隔离
            if self._health_service.should_quarantine_proxy(proxy):
                proxy.force_quarantine(
                    reason="Poor performance metrics",
                    duration_minutes=30
                )
            
            # 5. 保存更新
            await self._proxy_repository.save(proxy)
            
            # 6. 发布事件
            if self._event_publisher:
                domain_events = proxy.domain_events
                for event in domain_events:
                    await self._event_publisher.publish(event)
                proxy.clear_domain_events()
                
        except Exception as e:
            # 记录错误但不抛出异常，避免影响业务流程
            # TODO: 添加日志记录
            pass
    
    async def perform_health_check(self, request: HealthCheckRequest) -> Dict[str, Any]:
        """执行健康检查"""
        try:
            if request.proxy_id:
                # 单个代理健康检查
                proxy = await self._proxy_repository.find_by_id(request.proxy_id)
                if not proxy:
                    raise ProxyNotFoundError(str(request.proxy_id))
                
                result = await self._health_service.perform_comprehensive_health_check(
                    proxy, request.config
                )
                
                # 更新代理健康状态
                proxy.update_health_status(result)
                await self._proxy_repository.save(proxy)
                
                # 发布事件
                if self._event_publisher:
                    domain_events = proxy.domain_events
                    for event in domain_events:
                        await self._event_publisher.publish(event)
                    proxy.clear_domain_events()
                
                return {
                    'proxy_id': str(proxy.id),
                    'success': result.success,
                    'response_time': result.response_time,
                    'health_status': proxy.health_status.value,
                    'error_message': result.error_message
                }
            else:
                # 批量健康检查
                proxies_to_check = await self._proxy_repository.find_needing_health_check(
                    check_interval_minutes=5,
                    limit=50
                )
                
                if not proxies_to_check:
                    return {'message': 'No proxies need health check', 'checked_count': 0}
                
                results = await self._health_service.perform_batch_health_check(
                    proxies_to_check, request.config, max_concurrent=10
                )
                
                # 批量更新状态
                updated_count = 0
                for proxy, health_result in results:
                    proxy.update_health_status(health_result)
                    await self._proxy_repository.save(proxy)
                    updated_count += 1
                    
                    # 发布事件
                    if self._event_publisher:
                        domain_events = proxy.domain_events
                        for event in domain_events:
                            await self._event_publisher.publish(event)
                        proxy.clear_domain_events()
                
                return {
                    'message': f'Health check completed for {updated_count} proxies',
                    'checked_count': updated_count,
                    'total_candidates': len(proxies_to_check)
                }
                
        except (ProxyNotFoundError, ProxyPoolApplicationError):
            raise
        except Exception as e:
            raise ProxyPoolApplicationError(
                f"Health check failed: {str(e)}"
            ) from e
    
    async def get_proxy_pool_statistics(self) -> Dict[str, Any]:
        """获取代理池统计信息"""
        try:
            # 1. 获取所有代理
            all_proxies = await self._proxy_repository.find_all()
            
            if not all_proxies:
                return {
                    'total_proxies': 0,
                    'available_proxies': 0,
                    'health_summary': {},
                    'selection_statistics': {},
                    'pool_health_score': 0.0
                }
            
            # 2. 计算基础统计
            available_proxies = [p for p in all_proxies if p.is_available]
            
            # 3. 健康状态统计
            health_summary = self._health_service.get_health_summary(all_proxies)
            
            # 4. 选择统计
            selection_stats = self._selection_service.get_selection_statistics(all_proxies)
            
            # 5. 按协议和地域统计
            protocol_stats = {}
            country_stats = {}
            
            for proxy in all_proxies:
                # 协议统计
                protocol = proxy.configuration.endpoint.protocol.value
                if protocol not in protocol_stats:
                    protocol_stats[protocol] = {'total': 0, 'available': 0}
                protocol_stats[protocol]['total'] += 1
                if proxy.is_available:
                    protocol_stats[protocol]['available'] += 1
                
                # 国家统计
                if proxy.configuration.geo_location:
                    country = proxy.configuration.geo_location.country_code
                    if country not in country_stats:
                        country_stats[country] = {'total': 0, 'available': 0}
                    country_stats[country]['total'] += 1
                    if proxy.is_available:
                        country_stats[country]['available'] += 1
            
            return {
                'total_proxies': len(all_proxies),
                'available_proxies': len(available_proxies),
                'availability_rate': len(available_proxies) / len(all_proxies) if all_proxies else 0,
                'health_summary': health_summary,
                'selection_statistics': selection_stats,
                'protocol_distribution': protocol_stats,
                'country_distribution': country_stats,
                'pool_health_score': selection_stats.get('pool_health_score', 0.0),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise ProxyPoolApplicationError(
                f"Failed to get statistics: {str(e)}"
            ) from e
    
    async def remove_proxy(self, proxy_id: str) -> bool:
        """移除代理"""
        try:
            proxy_id_obj = ProxyId(proxy_id)
            return await self._proxy_repository.delete(proxy_id_obj)
        except Exception as e:
            raise ProxyPoolApplicationError(
                f"Failed to remove proxy: {str(e)}"
            ) from e
    
    async def cleanup_poor_proxies(
        self,
        min_success_rate: float = 0.1,
        max_consecutive_failures: int = 10,
        inactive_days: int = 7
    ) -> int:
        """清理表现差的代理"""
        try:
            inactive_since = datetime.utcnow() - timedelta(days=inactive_days)
            
            removed_count = await self._proxy_repository.delete_by_criteria(
                health_status=HealthStatus.QUARANTINED,
                inactive_since=inactive_since,
                success_rate_below=min_success_rate
            )
            
            return removed_count
            
        except Exception as e:
            raise ProxyPoolApplicationError(
                f"Failed to cleanup proxies: {str(e)}"
            ) from e
    
    async def update_proxy_configuration(
        self, 
        proxy_id: str, 
        new_config: ProxyConfiguration
    ) -> None:
        """更新代理配置"""
        try:
            proxy_id_obj = ProxyId(proxy_id)
            proxy = await self._proxy_repository.find_by_id(proxy_id_obj)
            
            if not proxy:
                raise ProxyNotFoundError(proxy_id)
            
            proxy.update_configuration(new_config)
            await self._proxy_repository.save(proxy)
            
        except (ProxyNotFoundError, ProxyPoolApplicationError):
            raise
        except Exception as e:
            raise ProxyPoolApplicationError(
                f"Failed to update proxy configuration: {str(e)}"
            ) from e