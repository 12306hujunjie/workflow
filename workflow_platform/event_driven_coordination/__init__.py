"""事件驱动协调模块

负责处理跨模块的事件驱动通信和协调
"""

from .coordinator import (
    EventDrivenCoordinator,
    get_coordinator,
    shutdown_coordinator,
    publish_event,
    publish_events,
    register_handler
)
from .event_bus import EventBus, EventBusFactory
from .event_handlers import (
    user_event_handlers,
    subscription_event_handlers,
    workflow_event_handlers,
    content_event_handlers
)

__all__ = [
    'EventDrivenCoordinator',
    'get_coordinator',
    'shutdown_coordinator',
    'publish_event',
    'publish_events',
    'register_handler',
    'EventBus',
    'EventBusFactory',
    'user_event_handlers',
    'subscription_event_handlers',
    'workflow_event_handlers',
    'content_event_handlers'
]