"""Domain entities for proxy pool."""

from .proxy import (
    ProxyId,
    Proxy,
    ProxyCreatedEvent,
    ProxyHealthChangedEvent,
    ProxyUsedEvent,
    ProxyQuarantinedEvent,
    ProxyRecoveredEvent,
)

__all__ = [
    'ProxyId',
    'Proxy',
    'ProxyCreatedEvent',
    'ProxyHealthChangedEvent',
    'ProxyUsedEvent',
    'ProxyQuarantinedEvent',
    'ProxyRecoveredEvent',
]