"""跨模块事件处理器

这个模块包含处理跨限界上下文事件的处理器，实现模块间的松耦合通信。
"""

from .user_event_handlers import (
    UserRegistrationEventHandler,
    UserStatusChangeEventHandler,
    UserLoginEventHandler
)
from .subscription_event_handlers import (
    SubscriptionActivationEventHandler,
    SubscriptionExpirationEventHandler
)
from .workflow_event_handlers import (
    WorkflowExecutionStartedEventHandler,
    WorkflowExecutionCompletedEventHandler
)
from .content_event_handlers import (
    ContentPublishedEventHandler,
    ContentModerationCompletedEventHandler
)

__all__ = [
    # 用户事件处理器
    'UserRegistrationEventHandler',
    'UserStatusChangeEventHandler', 
    'UserLoginEventHandler',
    
    # 订阅事件处理器
    'SubscriptionActivationEventHandler',
    'SubscriptionExpirationEventHandler',
    
    # 工作流事件处理器
    'WorkflowExecutionStartedEventHandler',
    'WorkflowExecutionCompletedEventHandler',
    
    # 内容事件处理器
    'ContentPublishedEventHandler',
    'ContentModerationCompletedEventHandler'
]