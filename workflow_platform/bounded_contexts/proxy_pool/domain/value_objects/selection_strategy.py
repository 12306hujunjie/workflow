"""Selection strategy value objects for proxy pool."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from ..exceptions import InvalidSelectionStrategyError


class SelectionStrategyType(Enum):
    """代理选择策略类型"""
    BEST = "best"                    # 选择最佳代理（基于综合评分）
    ROUND_ROBIN = "round_robin"      # 轮询选择
    RANDOM = "random"                # 随机选择
    WEIGHTED = "weighted"            # 权重选择（基于性能）
    GEO_PREFERRED = "geo_preferred"  # 地域优先选择
    LEAST_USED = "least_used"        # 最少使用选择
    FASTEST = "fastest"              # 最快响应选择
    MOST_RELIABLE = "most_reliable"  # 最可靠选择


class LoadBalancingMode(Enum):
    """负载均衡模式"""
    NONE = "none"                    # 不进行负载均衡
    CONCURRENT_LIMIT = "concurrent_limit"  # 基于并发限制
    REQUEST_RATE = "request_rate"    # 基于请求频率
    ADAPTIVE = "adaptive"            # 自适应负载均衡


@dataclass(frozen=True)
class GeoPreference:
    """地理位置偏好"""
    preferred_countries: List[str] = field(default_factory=list)
    preferred_regions: List[str] = field(default_factory=list)
    excluded_countries: List[str] = field(default_factory=list)
    excluded_regions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # 验证国家代码格式
        for country in self.preferred_countries + self.excluded_countries:
            if len(country) != 2:
                raise InvalidSelectionStrategyError(
                    f"Invalid country code: {country}. Must be 2 characters."
                )


@dataclass(frozen=True)
class PerformanceThreshold:
    """性能阈值"""
    min_success_rate: float = 0.8
    max_response_time: float = 5000.0  # milliseconds
    min_availability_score: float = 0.7
    max_consecutive_failures: int = 3
    
    def __post_init__(self):
        if not (0.0 <= self.min_success_rate <= 1.0):
            raise InvalidSelectionStrategyError(
                f"min_success_rate must be between 0.0 and 1.0, got {self.min_success_rate}"
            )
        
        if self.max_response_time <= 0:
            raise InvalidSelectionStrategyError(
                f"max_response_time must be positive, got {self.max_response_time}"
            )
        
        if not (0.0 <= self.min_availability_score <= 1.0):
            raise InvalidSelectionStrategyError(
                f"min_availability_score must be between 0.0 and 1.0, got {self.min_availability_score}"
            )
        
        if self.max_consecutive_failures < 0:
            raise InvalidSelectionStrategyError(
                f"max_consecutive_failures must be non-negative, got {self.max_consecutive_failures}"
            )


@dataclass(frozen=True)
class LoadBalancingConfig:
    """负载均衡配置"""
    mode: LoadBalancingMode = LoadBalancingMode.CONCURRENT_LIMIT
    max_concurrent_per_proxy: int = 10
    max_requests_per_minute: int = 60
    adaptive_threshold: float = 0.8
    
    def __post_init__(self):
        if self.max_concurrent_per_proxy <= 0:
            raise InvalidSelectionStrategyError(
                f"max_concurrent_per_proxy must be positive, got {self.max_concurrent_per_proxy}"
            )
        
        if self.max_requests_per_minute <= 0:
            raise InvalidSelectionStrategyError(
                f"max_requests_per_minute must be positive, got {self.max_requests_per_minute}"
            )
        
        if not (0.0 <= self.adaptive_threshold <= 1.0):
            raise InvalidSelectionStrategyError(
                f"adaptive_threshold must be between 0.0 and 1.0, got {self.adaptive_threshold}"
            )


@dataclass(frozen=True)
class SelectionStrategy:
    """代理选择策略配置"""
    strategy_type: SelectionStrategyType
    geo_preference: Optional[GeoPreference] = None
    performance_threshold: Optional[PerformanceThreshold] = None
    load_balancing: Optional[LoadBalancingConfig] = None
    fallback_strategy: Optional[SelectionStrategyType] = None
    weight_factors: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        # 设置默认值
        if self.performance_threshold is None:
            object.__setattr__(self, 'performance_threshold', PerformanceThreshold())
        
        if self.load_balancing is None:
            object.__setattr__(self, 'load_balancing', LoadBalancingConfig())
        
        # 设置默认权重因子
        default_weights = {
            'success_rate': 0.4,
            'response_time': 0.3,
            'stability': 0.2,
            'geo_preference': 0.1
        }
        
        if not self.weight_factors:
            object.__setattr__(self, 'weight_factors', default_weights)
        else:
            # 验证权重因子
            total_weight = sum(self.weight_factors.values())
            if abs(total_weight - 1.0) > 0.01:  # 允许小数点误差
                raise InvalidSelectionStrategyError(
                    f"Weight factors must sum to 1.0, got {total_weight}"
                )
    
    @classmethod
    def best_strategy(
        cls,
        geo_preference: Optional[GeoPreference] = None,
        performance_threshold: Optional[PerformanceThreshold] = None
    ) -> 'SelectionStrategy':
        """创建最佳选择策略"""
        return cls(
            strategy_type=SelectionStrategyType.BEST,
            geo_preference=geo_preference,
            performance_threshold=performance_threshold,
            fallback_strategy=SelectionStrategyType.ROUND_ROBIN
        )
    
    @classmethod
    def round_robin_strategy(
        cls,
        performance_threshold: Optional[PerformanceThreshold] = None
    ) -> 'SelectionStrategy':
        """创建轮询选择策略"""
        return cls(
            strategy_type=SelectionStrategyType.ROUND_ROBIN,
            performance_threshold=performance_threshold
        )
    
    @classmethod
    def geo_preferred_strategy(
        cls,
        preferred_countries: List[str],
        fallback_strategy: SelectionStrategyType = SelectionStrategyType.BEST
    ) -> 'SelectionStrategy':
        """创建地域优先选择策略"""
        geo_pref = GeoPreference(preferred_countries=preferred_countries)
        return cls(
            strategy_type=SelectionStrategyType.GEO_PREFERRED,
            geo_preference=geo_pref,
            fallback_strategy=fallback_strategy
        )
    
    @classmethod
    def fastest_strategy(
        cls,
        max_response_time: float = 3000.0
    ) -> 'SelectionStrategy':
        """创建最快响应选择策略"""
        threshold = PerformanceThreshold(max_response_time=max_response_time)
        weights = {
            'response_time': 0.6,
            'success_rate': 0.3,
            'stability': 0.1,
            'geo_preference': 0.0
        }
        return cls(
            strategy_type=SelectionStrategyType.FASTEST,
            performance_threshold=threshold,
            weight_factors=weights,
            fallback_strategy=SelectionStrategyType.BEST
        )
    
    @classmethod
    def most_reliable_strategy(
        cls,
        min_success_rate: float = 0.95
    ) -> 'SelectionStrategy':
        """创建最可靠选择策略"""
        threshold = PerformanceThreshold(min_success_rate=min_success_rate)
        weights = {
            'success_rate': 0.5,
            'stability': 0.4,
            'response_time': 0.1,
            'geo_preference': 0.0
        }
        return cls(
            strategy_type=SelectionStrategyType.MOST_RELIABLE,
            performance_threshold=threshold,
            weight_factors=weights,
            fallback_strategy=SelectionStrategyType.BEST
        )


@dataclass(frozen=True)
class SelectionContext:
    """选择上下文"""
    request_id: Optional[str] = None
    target_host: Optional[str] = None
    preferred_country: Optional[str] = None
    preferred_protocol: Optional[str] = None
    max_response_time: Optional[float] = None
    min_success_rate: Optional[float] = None
    exclude_proxy_ids: List[str] = field(default_factory=list)
    current_proxy_usage: Dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def with_exclusions(self, proxy_ids: List[str]) -> 'SelectionContext':
        """创建包含排除列表的新上下文"""
        return SelectionContext(
            request_id=self.request_id,
            target_host=self.target_host,
            preferred_country=self.preferred_country,
            preferred_protocol=self.preferred_protocol,
            max_response_time=self.max_response_time,
            min_success_rate=self.min_success_rate,
            exclude_proxy_ids=self.exclude_proxy_ids + proxy_ids,
            current_proxy_usage=self.current_proxy_usage.copy(),
            timestamp=self.timestamp,
            metadata=self.metadata.copy()
        )
    
    def with_preference(
        self, 
        country: Optional[str] = None,
        protocol: Optional[str] = None
    ) -> 'SelectionContext':
        """创建包含偏好的新上下文"""
        return SelectionContext(
            request_id=self.request_id,
            target_host=self.target_host,
            preferred_country=country or self.preferred_country,
            preferred_protocol=protocol or self.preferred_protocol,
            max_response_time=self.max_response_time,
            min_success_rate=self.min_success_rate,
            exclude_proxy_ids=self.exclude_proxy_ids.copy(),
            current_proxy_usage=self.current_proxy_usage.copy(),
            timestamp=self.timestamp,
            metadata=self.metadata.copy()
        )


@dataclass(frozen=True)
class ProxyFilters:
    """代理过滤器"""
    protocols: List[str] = field(default_factory=list)
    country_codes: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    anonymity_levels: List[int] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    min_success_rate: Optional[float] = None
    max_response_time: Optional[float] = None
    min_availability_score: Optional[float] = None
    exclude_quarantined: bool = True
    exclude_ids: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # 验证输入
        if self.min_success_rate is not None:
            if not (0.0 <= self.min_success_rate <= 1.0):
                raise InvalidSelectionStrategyError(
                    f"min_success_rate must be between 0.0 and 1.0"
                )
        
        if self.max_response_time is not None:
            if self.max_response_time <= 0:
                raise InvalidSelectionStrategyError(
                    f"max_response_time must be positive"
                )
        
        if self.min_availability_score is not None:
            if not (0.0 <= self.min_availability_score <= 1.0):
                raise InvalidSelectionStrategyError(
                    f"min_availability_score must be between 0.0 and 1.0"
                )
        
        for level in self.anonymity_levels:
            if level not in [1, 2, 3]:
                raise InvalidSelectionStrategyError(
                    f"anonymity_level must be 1, 2, or 3, got {level}"
                )
    
    @classmethod
    def for_country(cls, country_code: str) -> 'ProxyFilters':
        """创建国家过滤器"""
        return cls(country_codes=[country_code])
    
    @classmethod
    def for_protocol(cls, protocol: str) -> 'ProxyFilters':
        """创建协议过滤器"""
        return cls(protocols=[protocol])
    
    @classmethod
    def high_performance(cls) -> 'ProxyFilters':
        """创建高性能过滤器"""
        return cls(
            min_success_rate=0.9,
            max_response_time=3000.0,
            min_availability_score=0.8,
            anonymity_levels=[2, 3]  # 只要匿名和精英代理
        )
    
    @classmethod
    def reliable_only(cls) -> 'ProxyFilters':
        """创建可靠代理过滤器"""
        return cls(
            min_success_rate=0.95,
            min_availability_score=0.9,
            exclude_quarantined=True
        )