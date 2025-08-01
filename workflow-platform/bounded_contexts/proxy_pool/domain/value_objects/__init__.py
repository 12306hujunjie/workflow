"""Value objects for proxy pool domain."""

from .proxy_config import (
    ProxyProtocol,
    ProxyStatus,
    AnonymityLevel,
    SelectionStrategy as LegacySelectionStrategy,
    ProxyCredentials,
    GeoLocation,
    ProxyEndpoint,
    ProxyConfiguration,
    HealthCheckConfig,
)

from .proxy_metrics import (
    HealthStatus,
    RequestResult,
    RequestRecord,
    ProxyMetrics,
    SelectionWeight,
    HealthCheckResult,
)

from .selection_strategy import (
    SelectionStrategyType,
    LoadBalancingMode,
    GeoPreference,
    PerformanceThreshold,
    LoadBalancingConfig,
    SelectionStrategy,
    SelectionContext,
    ProxyFilters,
)

__all__ = [
    # proxy_config
    'ProxyProtocol',
    'ProxyStatus',
    'AnonymityLevel',
    'LegacySelectionStrategy',
    'ProxyCredentials',
    'GeoLocation',
    'ProxyEndpoint',
    'ProxyConfiguration',
    'HealthCheckConfig',
    
    # proxy_metrics
    'HealthStatus',
    'RequestResult',
    'RequestRecord',
    'ProxyMetrics',
    'SelectionWeight',
    'HealthCheckResult',
    
    # selection_strategy
    'SelectionStrategyType',
    'LoadBalancingMode',
    'GeoPreference',
    'PerformanceThreshold',
    'LoadBalancingConfig',
    'SelectionStrategy',
    'SelectionContext',
    'ProxyFilters',
]