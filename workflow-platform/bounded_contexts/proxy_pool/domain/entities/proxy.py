"""Proxy aggregate root - Core entity for proxy pool domain."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4

from shared_kernel.domain.base_entity import BaseEntity
from shared_kernel.domain.events.domain_event import DomainEvent

from ..value_objects import (
    ProxyConfiguration,
    ProxyMetrics,
    HealthStatus,
    HealthCheckResult,
    SelectionWeight,
    SelectionStrategy,
    SelectionContext,
    RequestResult
)
from ..exceptions import (
    ProxyHealthCheckError,
    ProxyQuarantineError,
    InvalidProxyConfigException
)


class ProxyId:
    """代理ID值对象"""
    
    def __init__(self, value: str):
        if not value or not isinstance(value, str):
            raise InvalidProxyConfigException("Proxy ID must be a non-empty string")
        self._value = value
    
    @property
    def value(self) -> str:
        return self._value
    
    def __str__(self) -> str:
        return self._value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, ProxyId):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    @classmethod
    def generate(cls) -> 'ProxyId':
        """生成新的代理ID"""
        return cls(str(uuid4()))
    
    @classmethod
    def from_endpoint(cls, host: str, port: int, protocol: str) -> 'ProxyId':
        """从端点信息生成代理ID"""
        return cls(f"{protocol}://{host}:{port}")


# Domain Events
class ProxyCreatedEvent(DomainEvent):
    """代理创建事件"""
    
    def __init__(self, proxy_id: ProxyId, configuration: ProxyConfiguration):
        super().__init__()
        self.proxy_id = proxy_id
        self.configuration = configuration


class ProxyHealthChangedEvent(DomainEvent):
    """代理健康状态改变事件"""
    
    def __init__(
        self, 
        proxy_id: ProxyId, 
        old_status: HealthStatus, 
        new_status: HealthStatus,
        check_result: Optional[HealthCheckResult] = None
    ):
        super().__init__()
        self.proxy_id = proxy_id
        self.old_status = old_status
        self.new_status = new_status
        self.check_result = check_result


class ProxyUsedEvent(DomainEvent):
    """代理使用事件"""
    
    def __init__(
        self, 
        proxy_id: ProxyId, 
        context: SelectionContext,
        selection_score: float
    ):
        super().__init__()
        self.proxy_id = proxy_id
        self.context = context
        self.selection_score = selection_score


class ProxyQuarantinedEvent(DomainEvent):
    """代理隔离事件"""
    
    def __init__(self, proxy_id: ProxyId, reason: str, metrics: ProxyMetrics):
        super().__init__()
        self.proxy_id = proxy_id
        self.reason = reason
        self.metrics = metrics


class ProxyRecoveredEvent(DomainEvent):
    """代理恢复事件"""
    
    def __init__(self, proxy_id: ProxyId, health_result: HealthCheckResult):
        super().__init__()
        self.proxy_id = proxy_id
        self.health_result = health_result


class Proxy(BaseEntity):
    """代理聚合根 - 管理代理的完整生命周期"""
    
    def __init__(
        self, 
        proxy_id: ProxyId, 
        configuration: ProxyConfiguration,
        created_at: Optional[datetime] = None
    ):
        super().__init__(proxy_id)
        self._configuration = configuration
        self._metrics = ProxyMetrics(first_seen=created_at or datetime.utcnow())
        self._health_status = HealthStatus.UNKNOWN
        self._selection_weight = SelectionWeight.default()
        self._current_concurrent_requests = 0
        self._last_health_check: Optional[HealthCheckResult] = None
        self._quarantine_until: Optional[datetime] = None
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = self._created_at
        
        # 发布创建事件
        self._add_domain_event(ProxyCreatedEvent(proxy_id, configuration))
    
    # Properties
    @property
    def id(self) -> ProxyId:
        """代理ID"""
        return self._id
    
    @property
    def configuration(self) -> ProxyConfiguration:
        """代理配置"""
        return self._configuration
    
    @property
    def metrics(self) -> ProxyMetrics:
        """代理指标"""
        return self._metrics
    
    @property
    def health_status(self) -> HealthStatus:
        """健康状态"""
        return self._health_status
    
    @property
    def selection_weight(self) -> SelectionWeight:
        """选择权重"""
        return self._selection_weight
    
    @property
    def current_concurrent_requests(self) -> int:
        """当前并发请求数"""
        return self._current_concurrent_requests
    
    @property
    def last_health_check(self) -> Optional[HealthCheckResult]:
        """最后健康检查结果"""
        return self._last_health_check
    
    @property
    def is_quarantined(self) -> bool:
        """是否被隔离"""
        if self._quarantine_until is None:
            return False
        return datetime.utcnow() < self._quarantine_until
    
    @property
    def is_available(self) -> bool:
        """是否可用"""
        return (
            not self.is_quarantined and
            self._health_status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED] and
            self._current_concurrent_requests < self._configuration.max_concurrent
        )
    
    @property
    def created_at(self) -> datetime:
        """创建时间"""
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        """更新时间"""
        return self._updated_at
    
    # Core Business Logic
    def update_health_status(self, health_result: HealthCheckResult) -> None:
        """更新健康状态"""
        old_status = self._health_status
        self._last_health_check = health_result
        
        if health_result.success:
            # 成功的健康检查
            if self._health_status == HealthStatus.QUARANTINED:
                self._recover_from_quarantine()
            elif health_result.response_time and health_result.response_time < 3000:
                self._health_status = HealthStatus.HEALTHY
            else:
                self._health_status = HealthStatus.DEGRADED
        else:
            # 失败的健康检查
            if self._metrics.consecutive_failures >= 3:
                self._health_status = HealthStatus.UNHEALTHY
            else:
                self._health_status = HealthStatus.DEGRADED
        
        self._updated_at = datetime.utcnow()
        
        # 发布状态改变事件
        if old_status != self._health_status:
            self._add_domain_event(
                ProxyHealthChangedEvent(self._id, old_status, self._health_status, health_result)
            )
    
    def record_request_result(
        self,
        success: bool,
        response_time: Optional[float] = None,
        http_status: Optional[int] = None,
        error_message: Optional[str] = None,
        target_host: Optional[str] = None
    ) -> None:
        """记录请求结果"""
        # 更新指标
        self._metrics = self._metrics.add_request_result(
            success=success,
            response_time=response_time,
            http_status=http_status,
            error_message=error_message,
            target_host=target_host
        )
        
        # 重新计算选择权重
        self._selection_weight = SelectionWeight.from_metrics(self._metrics)
        
        # 检查是否需要隔离
        if self._metrics.should_quarantine and not self.is_quarantined:
            self._quarantine("Automatic quarantine due to poor performance")
        
        # 更新健康状态
        old_status = self._health_status
        self._health_status = self._metrics.get_health_status()
        
        self._updated_at = datetime.utcnow()
        
        # 发布状态改变事件
        if old_status != self._health_status:
            self._add_domain_event(
                ProxyHealthChangedEvent(self._id, old_status, self._health_status)
            )
    
    def calculate_selection_score(
        self, 
        strategy: SelectionStrategy, 
        context: SelectionContext
    ) -> float:
        """计算选择评分"""
        if not self.is_available:
            return 0.0
        
        base_score = 0.0
        weights = strategy.weight_factors
        
        # 成功率评分
        if 'success_rate' in weights:
            base_score += self._metrics.success_rate * weights['success_rate']
        
        # 响应时间评分 (越快越好)
        if 'response_time' in weights and self._metrics.average_response_time > 0:
            # 3秒以下为满分，超过3秒按比例扣分
            max_time = 3000.0
            time_score = max(0, 1 - (self._metrics.average_response_time / max_time))
            base_score += time_score * weights['response_time']
        
        # 稳定性评分
        if 'stability' in weights:
            base_score += self._metrics.stability_index * weights['stability']
        
        # 地理位置偏好评分
        if 'geo_preference' in weights and strategy.geo_preference:
            geo_score = self._calculate_geo_preference_score(
                strategy.geo_preference, context
            )
            base_score += geo_score * weights['geo_preference']
        
        # 应用选择权重
        final_score = base_score * self._selection_weight.final_weight
        
        # 负载均衡调整
        if strategy.load_balancing:
            load_penalty = self._calculate_load_penalty(strategy.load_balancing)
            final_score *= (1 - load_penalty)
        
        return max(0.0, min(1.0, final_score))
    
    def _calculate_geo_preference_score(
        self, 
        geo_preference, 
        context: SelectionContext
    ) -> float:
        """计算地理偏好评分"""
        if not self._configuration.geo_location:
            return 0.5  # 无地理信息，给中等分
        
        score = 0.5  # 基础分
        
        # 检查首选国家
        if (geo_preference.preferred_countries and 
            self._configuration.geo_location.country_code in geo_preference.preferred_countries):
            score += 0.4
        
        # 检查上下文偏好
        if (context.preferred_country and 
            self._configuration.geo_location.country_code == context.preferred_country):
            score += 0.3
        
        # 检查排除国家
        if (geo_preference.excluded_countries and 
            self._configuration.geo_location.country_code in geo_preference.excluded_countries):
            score = 0.0
        
        return min(1.0, score)
    
    def _calculate_load_penalty(self, load_config) -> float:
        """计算负载惩罚"""
        if self._current_concurrent_requests == 0:
            return 0.0
        
        # 基于当前并发数的惩罚
        concurrent_ratio = self._current_concurrent_requests / self._configuration.max_concurrent
        return min(0.5, concurrent_ratio * 0.3)  # 最多50%惩罚
    
    def acquire_for_request(self, context: SelectionContext) -> None:
        """获取代理用于请求"""
        if not self.is_available:
            raise ProxyQuarantineError(
                str(self._id), 
                "Proxy is not available for requests"
            )
        
        if self._current_concurrent_requests >= self._configuration.max_concurrent:
            raise ProxyQuarantineError(
                str(self._id),
                f"Proxy has reached maximum concurrent requests ({self._configuration.max_concurrent})"
            )
        
        self._current_concurrent_requests += 1
        self._updated_at = datetime.utcnow()
        
        # 计算选择评分用于事件
        selection_score = self.calculate_selection_score(
            SelectionStrategy.best_strategy(), context
        )
        
        # 发布使用事件
        self._add_domain_event(ProxyUsedEvent(self._id, context, selection_score))
    
    def release_from_request(self) -> None:
        """释放代理请求"""
        if self._current_concurrent_requests > 0:
            self._current_concurrent_requests -= 1
            self._updated_at = datetime.utcnow()
    
    def mark_as_failed(self, failure_reason: str) -> None:
        """标记为失败"""
        old_status = self._health_status
        self._health_status = HealthStatus.UNHEALTHY
        self._updated_at = datetime.utcnow()
        
        # 发布状态改变事件
        self._add_domain_event(
            ProxyHealthChangedEvent(self._id, old_status, self._health_status)
        )
    
    def _quarantine(self, reason: str, duration_minutes: int = 30) -> None:
        """隔离代理"""
        self._quarantine_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self._health_status = HealthStatus.QUARANTINED
        self._updated_at = datetime.utcnow()
        
        # 发布隔离事件
        self._add_domain_event(ProxyQuarantinedEvent(self._id, reason, self._metrics))
    
    def _recover_from_quarantine(self) -> None:
        """从隔离中恢复"""
        if not self.is_quarantined:
            return
        
        self._quarantine_until = None
        self._health_status = HealthStatus.HEALTHY
        self._updated_at = datetime.utcnow()
        
        # 发布恢复事件
        if self._last_health_check:
            self._add_domain_event(ProxyRecoveredEvent(self._id, self._last_health_check))
    
    def force_quarantine(self, reason: str, duration_minutes: int = 60) -> None:
        """强制隔离代理"""
        self._quarantine(reason, duration_minutes)
    
    def force_recovery(self) -> None:
        """强制恢复代理"""
        self._recover_from_quarantine()
    
    def update_configuration(self, new_configuration: ProxyConfiguration) -> None:
        """更新代理配置"""
        if new_configuration.endpoint != self._configuration.endpoint:
            raise InvalidProxyConfigException(
                "Cannot change proxy endpoint after creation"
            )
        
        self._configuration = new_configuration
        self._updated_at = datetime.utcnow()
    
    def meets_filter_criteria(self, filters) -> bool:
        """检查是否满足过滤条件"""
        # 协议过滤
        if filters.protocols and self._configuration.endpoint.protocol.value not in filters.protocols:
            return False
        
        # 国家过滤
        if (filters.country_codes and self._configuration.geo_location and 
            self._configuration.geo_location.country_code not in filters.country_codes):
            return False
        
        # 性能过滤
        if filters.min_success_rate and self._metrics.success_rate < filters.min_success_rate:
            return False
        
        if (filters.max_response_time and self._metrics.average_response_time > 0 and
            self._metrics.average_response_time > filters.max_response_time):
            return False
        
        if (filters.min_availability_score and 
            self._metrics.availability_score < filters.min_availability_score):
            return False
        
        # 排除隔离的代理
        if filters.exclude_quarantined and self.is_quarantined:
            return False
        
        # 排除特定ID
        if filters.exclude_ids and str(self._id) in filters.exclude_ids:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': str(self._id),
            'configuration': self._configuration.to_dict(),
            'metrics': {
                'total_requests': self._metrics.total_requests,
                'success_rate': self._metrics.success_rate,
                'average_response_time': self._metrics.average_response_time,
                'availability_score': self._metrics.availability_score,
                'consecutive_failures': self._metrics.consecutive_failures,
                'last_success_time': self._metrics.last_success_time.isoformat() if self._metrics.last_success_time else None,
                'last_failure_time': self._metrics.last_failure_time.isoformat() if self._metrics.last_failure_time else None
            },
            'health_status': self._health_status.value,
            'is_quarantined': self.is_quarantined,
            'is_available': self.is_available,
            'current_concurrent_requests': self._current_concurrent_requests,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
    
    def __str__(self) -> str:
        return f"Proxy({self._id}, {self._configuration.endpoint.url}, {self._health_status.value})"
    
    def __repr__(self) -> str:
        return self.__str__()