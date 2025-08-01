"""Proxy pool facade - Simplified interface for other bounded contexts."""

from typing import Optional, List, Dict, Any
from datetime import datetime

from ...application.services import (
    ProxyPoolApplicationService,
    GetProxyRequest,
    AddProxyRequest,
    ReportResultRequest,
    HealthCheckRequest
)
from ...domain.value_objects import (
    ProxyConfiguration,
    ProxyProtocol,
    SelectionStrategy,
    SelectionStrategyType,
    SelectionContext,
    ProxyFilters,
    GeoPreference,
    PerformanceThreshold
)
from ...domain.exceptions import (
    NoAvailableProxyError,
    ProxySelectionError,
    ProxyPoolApplicationError
)


class ProxyInfo:
    """代理信息 - 对外简化的代理信息"""
    
    def __init__(
        self,
        proxy_id: str,
        host: str,
        port: int,
        protocol: str,
        url: str,
        health_status: str,
        response_time: Optional[float] = None,
        success_rate: Optional[float] = None,
        country: Optional[str] = None
    ):
        self.id = proxy_id
        self.host = host
        self.port = port
        self.protocol = protocol
        self.url = url
        self.health_status = health_status
        self.response_time = response_time
        self.success_rate = success_rate
        self.country = country
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'host': self.host,
            'port': self.port,
            'protocol': self.protocol,
            'url': self.url,
            'health_status': self.health_status,
            'response_time': self.response_time,
            'success_rate': self.success_rate,
            'country': self.country
        }


class ProxyPoolFacade:
    """代理池门面 - 对外统一接口"""
    
    def __init__(self, application_service: ProxyPoolApplicationService):
        self._application_service = application_service
    
    # === 核心获取代理接口 === #
    
    async def get_proxy(
        self,
        country_code: Optional[str] = None,
        protocol: Optional[ProxyProtocol] = None,
        strategy: SelectionStrategyType = SelectionStrategyType.BEST,
        min_success_rate: Optional[float] = None,
        max_response_time: Optional[float] = None
    ) -> Optional[ProxyInfo]:
        """获取代理 - 最简化接口"""
        try:
            # 构建过滤器
            filters = ProxyFilters(
                country_codes=[country_code] if country_code else [],
                protocols=[protocol.value] if protocol else [],
                min_success_rate=min_success_rate,
                max_response_time=max_response_time
            )
            
            # 构建选择策略
            selection_strategy = SelectionStrategy(strategy_type=strategy)
            if country_code:
                selection_strategy = SelectionStrategy.geo_preferred_strategy([country_code])
            
            # 构建上下文
            context = SelectionContext(
                preferred_country=country_code,
                preferred_protocol=protocol.value if protocol else None,
                timestamp=datetime.utcnow()
            )
            
            # 获取代理
            request = GetProxyRequest(
                filters=filters,
                selection_strategy=selection_strategy,
                context=context
            )
            
            response = await self._application_service.get_available_proxy(request)
            
            # 转换为简化的代理信息
            proxy = response.proxy
            return ProxyInfo(
                proxy_id=str(proxy.id),
                host=proxy.configuration.endpoint.host,
                port=proxy.configuration.endpoint.port,
                protocol=proxy.configuration.endpoint.protocol.value,
                url=proxy.configuration.url,
                health_status=proxy.health_status.value,
                response_time=proxy.metrics.average_response_time,
                success_rate=proxy.metrics.success_rate,
                country=proxy.configuration.geo_location.country_code if proxy.configuration.geo_location else None
            )
            
        except NoAvailableProxyError:
            return None
        except Exception as e:
            # 记录错误但不抛出异常，保证其他服务的健壮性
            # TODO: 添加结构化日志
            return None
    
    async def get_best_proxy(
        self,
        country_code: Optional[str] = None,
        protocol: Optional[ProxyProtocol] = None
    ) -> Optional[ProxyInfo]:
        """获取最佳代理"""
        return await self.get_proxy(
            country_code=country_code,
            protocol=protocol,
            strategy=SelectionStrategyType.BEST
        )
    
    async def get_fastest_proxy(
        self,
        country_code: Optional[str] = None,
        protocol: Optional[ProxyProtocol] = None,
        max_response_time: float = 3000.0
    ) -> Optional[ProxyInfo]:
        """获取最快代理"""
        return await self.get_proxy(
            country_code=country_code,
            protocol=protocol,
            strategy=SelectionStrategyType.FASTEST,
            max_response_time=max_response_time
        )
    
    async def get_most_reliable_proxy(
        self,
        country_code: Optional[str] = None,
        protocol: Optional[ProxyProtocol] = None,
        min_success_rate: float = 0.95
    ) -> Optional[ProxyInfo]:
        """获取最可靠代理"""
        return await self.get_proxy(
            country_code=country_code,
            protocol=protocol,
            strategy=SelectionStrategyType.MOST_RELIABLE,
            min_success_rate=min_success_rate
        )
    
    async def get_random_proxy(
        self,
        country_code: Optional[str] = None,
        protocol: Optional[ProxyProtocol] = None
    ) -> Optional[ProxyInfo]:
        """获取随机代理"""
        return await self.get_proxy(
            country_code=country_code,
            protocol=protocol,
            strategy=SelectionStrategyType.RANDOM
        )
    
    # === 结果报告接口 === #
    
    async def report_success(
        self,
        proxy_id: str,
        response_time: Optional[float] = None,
        target_host: Optional[str] = None
    ) -> None:
        """报告成功结果"""
        await self.report_result(
            proxy_id=proxy_id,
            success=True,
            response_time=response_time,
            target_host=target_host
        )
    
    async def report_failure(
        self,
        proxy_id: str,
        error_message: Optional[str] = None,
        http_status: Optional[int] = None,
        target_host: Optional[str] = None
    ) -> None:
        """报告失败结果"""
        await self.report_result(
            proxy_id=proxy_id,
            success=False,
            error_message=error_message,
            http_status=http_status,
            target_host=target_host
        )
    
    async def report_result(
        self,
        proxy_id: str,
        success: bool,
        response_time: Optional[float] = None,
        http_status: Optional[int] = None,
        error_message: Optional[str] = None,
        target_host: Optional[str] = None
    ) -> None:
        """报告使用结果"""
        try:
            request = ReportResultRequest(
                proxy_id=proxy_id,
                success=success,
                response_time=response_time,
                http_status=http_status,
                error_message=error_message,
                target_host=target_host
            )
            
            await self._application_service.report_proxy_result(request)
            
        except Exception as e:
            # 不抛出异常，避免影响业务流程
            # TODO: 添加结构化日志
            pass
    
    # === 管理接口 === #
    
    async def add_proxy(
        self,
        host: str,
        port: int,
        protocol: ProxyProtocol,
        username: Optional[str] = None,
        password: Optional[str] = None,
        country: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """添加代理"""
        from ...domain.value_objects import (
            ProxyEndpoint,
            ProxyCredentials,
            GeoLocation
        )
        
        try:
            # 构建配置
            endpoint = ProxyEndpoint(host=host, port=port, protocol=protocol)
            
            credentials = None
            if username and password:
                credentials = ProxyCredentials(username=username, password=password)
            
            geo_location = None
            if country:
                geo_location = GeoLocation(country_code=country)
            
            configuration = ProxyConfiguration(
                endpoint=endpoint,
                credentials=credentials,
                geo_location=geo_location,
                tags=tags or []
            )
            
            request = AddProxyRequest(configuration)
            proxy_id = await self._application_service.add_proxy(request)
            
            return str(proxy_id)
            
        except Exception as e:
            raise ProxyPoolApplicationError(f"Failed to add proxy: {str(e)}") from e
    
    async def remove_proxy(self, proxy_id: str) -> bool:
        """移除代理"""
        try:
            return await self._application_service.remove_proxy(proxy_id)
        except Exception as e:
            # TODO: 添加日志
            return False
    
    async def get_proxy_statistics(self) -> Dict[str, Any]:
        """获取代理池统计"""
        try:
            return await self._application_service.get_proxy_pool_statistics()
        except Exception as e:
            return {
                'error': str(e),
                'total_proxies': 0,
                'available_proxies': 0
            }
    
    async def perform_health_check(
        self, 
        proxy_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行健康检查"""
        try:
            request = HealthCheckRequest(proxy_id=proxy_id)
            return await self._application_service.perform_health_check(request)
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    # === 便利方法 === #
    
    async def is_available(self) -> bool:
        """检查代理池是否可用"""
        try:
            stats = await self.get_proxy_statistics()
            return stats.get('available_proxies', 0) > 0
        except:
            return False
    
    async def get_available_countries(self) -> List[str]:
        """获取可用的国家列表"""
        try:
            stats = await self.get_proxy_statistics()
            country_dist = stats.get('country_distribution', {})
            return [
                country for country, info in country_dist.items()
                if info.get('available', 0) > 0
            ]
        except:
            return []
    
    async def get_available_protocols(self) -> List[str]:
        """获取可用的协议列表"""
        try:
            stats = await self.get_proxy_statistics()
            protocol_dist = stats.get('protocol_distribution', {})
            return [
                protocol for protocol, info in protocol_dist.items()
                if info.get('available', 0) > 0
            ]
        except:
            return []
    
    # === 高级用例 === #
    
    async def get_proxy_with_retry(
        self,
        country_code: Optional[str] = None,
        protocol: Optional[ProxyProtocol] = None,
        max_retries: int = 3,
        exclude_ids: Optional[List[str]] = None
    ) -> Optional[ProxyInfo]:
        """带重试的获取代理"""
        exclude_list = exclude_ids or []
        
        for attempt in range(max_retries):
            try:
                # 构建上下文，排除已失败的代理
                context = SelectionContext(
                    preferred_country=country_code,
                    preferred_protocol=protocol.value if protocol else None,
                    exclude_proxy_ids=exclude_list
                )
                
                filters = ProxyFilters(
                    country_codes=[country_code] if country_code else [],
                    protocols=[protocol.value] if protocol else [],
                    exclude_ids=exclude_list
                )
                
                request = GetProxyRequest(
                    filters=filters,
                    selection_strategy=SelectionStrategy.best_strategy(),
                    context=context
                )
                
                response = await self._application_service.get_available_proxy(request)
                
                proxy = response.proxy
                return ProxyInfo(
                    proxy_id=str(proxy.id),
                    host=proxy.configuration.endpoint.host,
                    port=proxy.configuration.endpoint.port,
                    protocol=proxy.configuration.endpoint.protocol.value,
                    url=proxy.configuration.url,
                    health_status=proxy.health_status.value,
                    response_time=proxy.metrics.average_response_time,
                    success_rate=proxy.metrics.success_rate,
                    country=proxy.configuration.geo_location.country_code if proxy.configuration.geo_location else None
                )
                
            except (NoAvailableProxyError, ProxySelectionError):
                if attempt == max_retries - 1:
                    return None
                continue
            except Exception:
                if attempt == max_retries - 1:
                    return None
                continue
        
        return None
    
    async def test_proxy_connectivity(self, proxy_id: str) -> Dict[str, Any]:
        """测试特定代理的连接性"""
        return await self.perform_health_check(proxy_id)