# Workflow Platform 架构重构方案

## 1. 重构目标

基于对现有架构的深入分析，本次重构旨在解决以下核心问题：
- 领域边界划分不够清晰，存在冗余
- 架构层次过于复杂，可能存在过度工程化
- 数据库设计与DDD聚合根概念不够匹配
- 事件驱动架构中领域事件与技术事件混淆
- API设计缺乏统一性和版本控制策略

## 2. 新架构设计

### 2.1 重新设计的领域边界

**调整前的7个领域：**
- User Management（用户管理）
- Subscription（订阅管理）
- Xiaohongshu（小红书）
- Qidian（起点）
- Proxy Pool（代理池）
- Workflow（工作流）
- Notification（通知）

**调整后的5个核心领域：**
1. **User Management Domain**（用户管理域）
   - 职责：用户注册、认证、授权、个人资料管理
   - 聚合根：User

2. **Subscription Domain**（订阅管理域）
   - 职责：服务订阅、计费、使用量统计
   - 聚合根：Subscription

3. **Platform Service Domain**（平台服务域）
   - 职责：统一管理各种第三方平台（小红书、起点等）的数据采集和内容管理
   - 聚合根：PlatformAccount, PlatformContent
   - 说明：合并原小红书和起点领域，提供统一的平台服务抽象

4. **Workflow Definition Domain**（工作流定义域）
   - 职责：工作流模板定义、规则配置
   - 聚合根：WorkflowDefinition

5. **Workflow Execution Domain**（工作流执行域）
   - 职责：工作流实例执行、状态管理、结果处理
   - 聚合根：WorkflowExecution

**基础设施服务（移至 shared_kernel/infrastructure）：**
- **Proxy Pool Service**：代理池管理和分配
- **Notification Service**：消息通知服务

### 2.2 新目录结构

```
workflow-platform/
├── bounded_contexts/
│   ├── user_management/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   ├── user.py
│   │   │   │   └── user_profile.py
│   │   │   ├── value_objects/
│   │   │   ├── repositories/
│   │   │   └── services/
│   │   ├── application/
│   │   │   ├── use_cases/
│   │   │   ├── services/
│   │   │   └── dto/
│   │   ├── infrastructure/
│   │   │   ├── models/
│   │   │   ├── repositories/
│   │   │   └── external_services/
│   │   └── presentation/
│   │       ├── routers/
│   │       └── schemas/
│   ├── subscription/
│   │   └── [同样的结构]
│   ├── platform_service/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   ├── platform_account.py
│   │   │   │   ├── platform_content.py
│   │   │   │   └── platform_config.py
│   │   │   └── services/
│   │   │       ├── xiaohongshu_service.py
│   │   │       └── qidian_service.py
│   │   └── [其他层级]
│   ├── workflow_definition/
│   │   └── [同样的结构]
│   └── workflow_execution/
│       └── [同样的结构]
├── shared_kernel/
│   ├── domain/
│   │   ├── events/
│   │   │   ├── domain_event.py
│   │   │   └── event_store.py
│   │   └── value_objects/
│   ├── application/
│   │   └── services/
│   └── infrastructure/
│       ├── proxy_pool/
│       │   ├── proxy_manager.py
│       │   ├── proxy_pool.py
│       │   └── usage_tracker.py
│       ├── notification/
│       │   ├── notification_service.py
│       │   └── channels/
│       ├── database/
│       ├── cache/
│       └── messaging/
└── event_driven_coordination/
    ├── domain_events/
    │   ├── handlers/
    │   └── processors/
    └── technical_workflows/
        ├── prefect_flows/
        └── task_orchestration/
```

## 3. 数据库设计优化

### 3.1 聚合根导向的表设计

**用户管理域：**
```sql
-- 用户聚合根
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**订阅管理域：**
```sql
-- 订阅聚合根
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    service_type VARCHAR(50) NOT NULL,
    plan_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE subscription_usage_stats (
    id UUID PRIMARY KEY,
    subscription_id UUID REFERENCES subscriptions(id),
    feature_name VARCHAR(100) NOT NULL,
    usage_count INTEGER DEFAULT 0,
    usage_limit INTEGER,
    reset_period VARCHAR(20),
    last_reset_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**平台服务域：**
```sql
-- 平台账户聚合根
CREATE TABLE platform_accounts (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    platform_type VARCHAR(50) NOT NULL, -- 'xiaohongshu', 'qidian', etc.
    account_identifier VARCHAR(255) NOT NULL,
    account_config JSONB,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, platform_type, account_identifier)
);

-- 平台内容聚合根
CREATE TABLE platform_contents (
    id UUID PRIMARY KEY,
    platform_account_id UUID REFERENCES platform_accounts(id),
    content_type VARCHAR(50) NOT NULL,
    content_id VARCHAR(255) NOT NULL,
    content_data JSONB NOT NULL,
    collected_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform_account_id, content_type, content_id)
);
```

### 3.2 领域事件存储

```sql
-- 领域事件存储
CREATE TABLE domain_events (
    id UUID PRIMARY KEY,
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    event_version INTEGER NOT NULL,
    occurred_at TIMESTAMP NOT NULL,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_domain_events_aggregate ON domain_events(aggregate_id, aggregate_type);
CREATE INDEX idx_domain_events_type ON domain_events(event_type);
CREATE INDEX idx_domain_events_occurred ON domain_events(occurred_at);
```

## 4. 事件驱动架构优化

### 4.1 领域事件与技术事件分离

**领域事件（Domain Events）：**
- `UserRegistered`：用户注册完成
- `SubscriptionActivated`：订阅激活
- `PlatformAccountConnected`：平台账户连接
- `WorkflowDefinitionCreated`：工作流定义创建
- `WorkflowExecutionCompleted`：工作流执行完成

**技术工作流事件（Technical Workflow Events）：**
- Prefect相关的任务编排事件
- 系统监控和运维事件
- 定时任务触发事件

### 4.2 事件处理架构

```python
# shared_kernel/domain/events/domain_event.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any
from uuid import UUID, uuid4

class DomainEvent(ABC):
    def __init__(self, aggregate_id: UUID, event_data: Dict[str, Any]):
        self.id = uuid4()
        self.aggregate_id = aggregate_id
        self.event_data = event_data
        self.occurred_at = datetime.utcnow()
        self.event_version = 1
    
    @property
    @abstractmethod
    def event_type(self) -> str:
        pass
    
    @property
    @abstractmethod
    def aggregate_type(self) -> str:
        pass

# 事件存储接口
class EventStore(ABC):
    @abstractmethod
    async def save_event(self, event: DomainEvent) -> None:
        pass
    
    @abstractmethod
    async def get_events(self, aggregate_id: UUID) -> List[DomainEvent]:
        pass
```

## 5. API设计统一化

### 5.1 统一的API规范

**命名规范：**
- 资源名使用复数形式：`/api/v1/users`, `/api/v1/subscriptions`
- 使用标准HTTP方法：GET, POST, PUT, PATCH, DELETE
- 路径参数使用kebab-case：`/api/v1/platform-accounts`

**版本控制：**
- URL版本控制：`/api/v1/`, `/api/v2/`
- 支持多版本并存
- 向后兼容策略

**统一响应格式：**
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid"
}

{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "输入数据验证失败",
    "details": []
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid"
}
```

### 5.2 重新组织的API路由

```python
# api_gateway/routers/v1.py
from fastapi import APIRouter

api_v1 = APIRouter(prefix="/api/v1")

# 用户管理域
api_v1.include_router(
    user_management_router, 
    prefix="/users", 
    tags=["用户管理"]
)

# 订阅管理域
api_v1.include_router(
    subscription_router, 
    prefix="/subscriptions", 
    tags=["订阅管理"]
)

# 平台服务域
api_v1.include_router(
    platform_service_router, 
    prefix="/platform-services", 
    tags=["平台服务"]
)

# 工作流定义域
api_v1.include_router(
    workflow_definition_router, 
    prefix="/workflow-definitions", 
    tags=["工作流定义"]
)

# 工作流执行域
api_v1.include_router(
    workflow_execution_router, 
    prefix="/workflow-executions", 
    tags=["工作流执行"]
)
```

## 6. 实施计划

### 第一阶段：目录结构重构（1-2周）

**任务清单：**
- [ ] 创建新的bounded_contexts目录结构
- [ ] 迁移代理池相关代码到shared_kernel/infrastructure/proxy_pool
- [ ] 迁移通知相关代码到shared_kernel/infrastructure/notification
- [ ] 合并xiaohongshu和qidian为platform_service域
- [ ] 拆分workflow为workflow_definition和workflow_execution
- [ ] 更新import路径和依赖关系

**验收标准：**
- 新目录结构创建完成
- 所有代码文件迁移到正确位置
- 项目能够正常启动和运行
- 所有测试通过

### 第二阶段：数据库重构（2-3周）

**任务清单：**
- [ ] 设计新的数据库schema
- [ ] 创建domain_events表
- [ ] 重新设计聚合根相关表结构
- [ ] 编写数据迁移脚本
- [ ] 更新ORM模型定义
- [ ] 更新仓储实现

**验收标准：**
- 新数据库schema部署完成
- 数据迁移成功，无数据丢失
- 所有CRUD操作正常
- 性能测试通过

### 第三阶段：事件驱动架构重构（2-3周）

**任务清单：**
- [ ] 实现领域事件基础设施
- [ ] 重构现有事件处理逻辑
- [ ] 分离领域事件和技术工作流事件
- [ ] 实现事件存储和重放机制
- [ ] 更新事件处理器

**验收标准：**
- 领域事件正确触发和处理
- 事件存储机制工作正常
- 系统最终一致性得到保证
- 事件重放功能可用

### 第四阶段：API统一化（1-2周）

**任务清单：**
- [ ] 重新设计API路由结构
- [ ] 统一API响应格式
- [ ] 实现版本控制机制
- [ ] 更新API文档
- [ ] 实现细粒度权限控制

**验收标准：**
- API设计符合RESTful规范
- 版本控制机制工作正常
- API文档完整准确
- 权限控制功能正常

## 7. 风险评估与应对

### 7.1 技术风险

**风险：数据迁移过程中可能出现数据丢失**
- 应对：制定详细的备份和回滚计划
- 应对：在测试环境充分验证迁移脚本
- 应对：采用渐进式迁移，分批处理数据

**风险：重构过程中可能引入新的bug**
- 应对：保持高测试覆盖率
- 应对：采用feature flag控制新功能发布
- 应对：建立完善的监控和告警机制

### 7.2 团队风险

**风险：团队成员需要学习新的架构模式**
- 应对：组织DDD和事件驱动架构培训
- 应对：编写详细的开发文档和最佳实践
- 应对：安排代码review和知识分享

**风险：重构期间可能影响开发效率**
- 应对：合理安排重构时间，避免与紧急需求冲突
- 应对：采用渐进式重构，保持系统可用性
- 应对：建立清晰的沟通机制

## 8. 预期收益

### 8.1 短期收益（3-6个月）
- 代码结构更清晰，新人上手更容易
- 领域边界明确，减少跨团队协调成本
- API设计统一，前端开发效率提升

### 8.2 长期收益（6-12个月）
- 系统可维护性显著提升
- 新功能开发速度加快
- 系统稳定性和可扩展性增强
- 技术债务减少

## 9. 总结

本次架构重构是一个系统性的改进项目，旨在解决现有架构中的关键问题，提升系统的整体质量。通过重新设计领域边界、优化数据库结构、简化事件驱动架构和统一API设计，我们将构建一个更加清晰、可维护和可扩展的系统架构。

重构过程需要团队的密切配合和持续投入，但长期来看，这将为项目的可持续发展奠定坚实的基础。