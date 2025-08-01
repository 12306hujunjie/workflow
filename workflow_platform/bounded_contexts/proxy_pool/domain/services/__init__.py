"""Domain services for proxy pool."""

from .proxy_selection_service import (
    ISelectionAlgorithm,
    BestProxySelectionAlgorithm,
    RoundRobinSelectionAlgorithm,
    WeightedRandomSelectionAlgorithm,
    GeoPreferredSelectionAlgorithm,
    LeastUsedSelectionAlgorithm,
    FastestSelectionAlgorithm,
    MostReliableSelectionAlgorithm,
    ProxySelectionService,
)

from .proxy_health_service import (
    IProxyHealthChecker,
    ProxyHealthService,
)

__all__ = [
    # Selection algorithms
    'ISelectionAlgorithm',
    'BestProxySelectionAlgorithm',
    'RoundRobinSelectionAlgorithm', 
    'WeightedRandomSelectionAlgorithm',
    'GeoPreferredSelectionAlgorithm',
    'LeastUsedSelectionAlgorithm',
    'FastestSelectionAlgorithm',
    'MostReliableSelectionAlgorithm',
    'ProxySelectionService',
    
    # Health service
    'IProxyHealthChecker',
    'ProxyHealthService',
]