# 事件驱动协调模块

本模块实现了完整的事件驱动架构，用于处理跨模块的松耦合通信和协调。

## 架构概述

事件驱动架构包含以下核心组件：

- **DomainEventModel**: 领域事件的数据库模型，用于持久化存储
- **EventStore**: 事件存储接口，支持 SQL 和内存存储
- **EventPublisher**: 事件发布器，基于 Redis Pub/Sub 实现异步发布
- **EventBus**: 事件总线，协调事件的存储、发布和处理
- **EventDrivenCoordinator**: 核心协调器，管理整个事件驱动架构
- **Event Handlers**: 跨模块事件处理器，实现业务逻辑解耦

## 快速开始

### 1. 初始化协调器

```python
from event_driven_coordination import get_coordinator, shutdown_coordinator

# 获取协调器实例
coordinator = await get_coordinator()

# 应用关闭时清理资源
await shutdown_coordinator()
```

### 2. 发布事件

```python
from event_driven_coordination import publish_event
from shared_kernel.domain.events.domain_event import GenericDomainEvent
from uuid import uuid4
from datetime import datetime

# 创建事件
event = GenericDomainEvent(
    aggregate_id=uuid4(),
    event_type="UserRegistered",
    event_data={
        "user_id": str(uuid4()),
        "email": "user@example.com",
        "username": "newuser"
    },
    occurred_at=datetime.utcnow()
)

# 发布事件
await publish_event(event)
```

### 3. 注册事件处理器

```python
from event_driven_coordination import register_handler
from shared_kernel.domain.events.event_handler import EventHandler

class MyEventHandler(EventHandler):
    async def handle(self, event):
        print(f"Handling event: {event.event_type}")
        # 处理业务逻辑

# 注册处理器
handler = MyEventHandler()
await register_handler("UserRegistered", handler)
```

## 生命周期管理

### FastAPI 集成示例

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from event_driven_coordination import get_coordinator, shutdown_coordinator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    await get_coordinator()
    yield
    # 关闭时清理
    await shutdown_coordinator()

app = FastAPI(lifespan=lifespan)
```

## 事件类型和处理器

### 用户模块事件

- **UserRegistered**: 用户注册事件
- **UserStatusChanged**: 用户状态变更事件
- **UserLoggedIn**: 用户登录事件

### 订阅模块事件

- **SubscriptionActivated**: 订阅激活事件
- **SubscriptionExpired**: 订阅过期事件

### 工作流模块事件

- **WorkflowExecutionStarted**: 工作流执行开始事件
- **WorkflowExecutionCompleted**: 工作流执行完成事件
- **WorkflowExecutionFailed**: 工作流执行失败事件

### 内容模块事件

- **ContentPublished**: 内容发布事件
- **ContentModerationCompleted**: 内容审核完成事件
- **ContentDeleted**: 内容删除事件

## 配置

### 数据库配置

事件存储使用 PostgreSQL 数据库，配置在 `shared_kernel/infrastructure/database/async_session.py` 中：

```python
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
```

### Redis 配置

事件发布使用 Redis，默认配置：

```python
REDIS_URL = "redis://localhost:6379/0"
```

## 监控和诊断

### 获取协调器状态

```python
coordinator = await get_coordinator()
status = await coordinator.get_coordinator_status()
print(status)
```

### 查询事件历史

```python
# 获取最近的事件
recent_events = await coordinator.get_event_history(limit=10)

# 获取特定类型的事件
user_events = await coordinator.get_event_history(
    event_type="UserRegistered",
    limit=5
)

# 获取特定聚合的事件
aggregate_events = await coordinator.get_event_history(
    aggregate_id=some_uuid
)
```

### 事件重放

```python
# 重放特定时间范围的事件
from datetime import datetime, timedelta

start_time = datetime.utcnow() - timedelta(hours=1)
end_time = datetime.utcnow()

await coordinator.replay_events(
    start_time=start_time,
    end_time=end_time,
    event_type="UserRegistered"  # 可选，重放特定类型的事件
)
```

## 最佳实践

### 1. 事件设计原则

- **事件不可变**: 一旦发布，事件数据不应修改
- **事件自包含**: 事件应包含处理所需的所有信息
- **事件命名**: 使用过去时态，如 "UserRegistered" 而不是 "RegisterUser"
- **版本控制**: 为事件数据结构变更做好版本控制准备

### 2. 处理器设计原则

- **幂等性**: 处理器应能安全地重复执行
- **错误处理**: 实现适当的错误处理和重试机制
- **性能考虑**: 避免在处理器中执行长时间运行的操作
- **依赖最小化**: 减少处理器之间的依赖关系

### 3. 错误处理

```python
class RobustEventHandler(EventHandler):
    async def handle(self, event):
        try:
            # 业务逻辑
            await self.process_event(event)
        except Exception as e:
            # 记录错误
            logger.error(f"Failed to handle event {event.event_type}: {e}")
            # 可以选择重新抛出异常或返回错误状态
            raise
    
    async def process_event(self, event):
        # 实际的业务逻辑
        pass
```

### 4. 性能优化

- **批量处理**: 使用 `publish_events` 批量发布事件
- **异步处理**: 所有事件处理都是异步的
- **连接池**: Redis 和数据库连接使用连接池
- **索引优化**: 数据库表已创建适当的索引

## 故障排除

### 常见问题

1. **事件未被处理**
   - 检查处理器是否正确注册
   - 验证 Redis 连接是否正常
   - 查看日志中的错误信息

2. **数据库连接问题**
   - 确认数据库配置正确
   - 检查数据库表是否已创建
   - 验证数据库权限

3. **Redis 连接问题**
   - 确认 Redis 服务运行正常
   - 检查 Redis 配置
   - 验证网络连接

### 调试技巧

```python
# 启用详细日志
import logging
logging.getLogger('event_driven_coordination').setLevel(logging.DEBUG)

# 检查未处理的事件
unprocessed_events = await coordinator.event_store.get_unprocessed_events()
print(f"Unprocessed events: {len(unprocessed_events)}")

# 检查事件发布器状态
publisher_status = await coordinator.event_publisher.health_check()
print(f"Publisher status: {publisher_status}")
```

## 扩展和定制

### 自定义事件处理器

```python
from shared_kernel.domain.events.event_handler import EventHandler

class CustomEventHandler(EventHandler):
    def __init__(self, custom_service):
        self.custom_service = custom_service
    
    async def handle(self, event):
        # 自定义处理逻辑
        await self.custom_service.process(event)

# 注册自定义处理器
handler = CustomEventHandler(my_service)
await register_handler("CustomEvent", handler)
```

### 自定义中间件

```python
from event_driven_coordination.event_bus import EventBusMiddleware

class CustomMiddleware(EventBusMiddleware):
    async def before_publish(self, event):
        # 发布前处理
        print(f"Publishing event: {event.event_type}")
        return event
    
    async def after_publish(self, event, result):
        # 发布后处理
        print(f"Published event: {event.event_type}")
        return result

# 添加中间件
coordinator = await get_coordinator()
coordinator.event_bus.add_middleware(CustomMiddleware())
```

## 示例代码

完整的示例代码请参考 `examples/startup_example.py` 文件。