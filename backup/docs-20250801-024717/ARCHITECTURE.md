# 服务导向自动化工作流平台详细设计方案

## 📋 项目概述

**目标**: 构建一个基于DDD+事件驱动架构的SaaS自动化工作流平台，支持多平台数据采集、用户订阅计费、智能代理池管理等功能。

**核心价值**: 
- 为用户提供小红书、起点等平台的自动化数据采集服务
- 基于订阅模式的差异化功能和配额管理
- 事件驱动的高响应性和可扩展性架构

## 🏗️ 技术栈选型

### 核心框架
```
FastAPI 0.104+          # 现代异步Web框架
SQLAlchemy 2.0          # 异步ORM，完整类型支持
Pydantic v2             # 数据验证，Rust内核性能
Dependency Injector     # 企业级依赖注入容器
Prefect 3.0             # 事件驱动工作流编排
```

### 基础设施
```
PostgreSQL 15+          # 主数据库，支持JSON和异步
Redis 7+                # 缓存、会话、消息队列、代理池状态
Playwright              # Web自动化和反检测
支付宝/微信支付 SDK      # 国内支付集成
```

## 🎯 DDD领域设计

### 领域边界识别
```
├── 用户管理域 (User Management BC)
│   └── 职责: 用户注册、认证、基础权限
├── 订阅计费域 (Subscription BC) 
│   └── 职责: 套餐管理、订阅状态、支付处理、配额控制
├── 小红书域 (Xiaohongshu BC)
│   └── 职责: 账号管理、内容采集、私信管理、数据分析
├── 起点域 (Qidian BC)
│   └── 职责: 小说数据采集、排行榜监控、作者信息
├── 代理池域 (Proxy Pool BC)
│   └── 职责: 代理管理、健康检查、智能轮换、地域分配
├── 工作流域 (Workflow BC)
│   └── 职责: 任务编排、调度策略、执行监控、故障恢复
└── 通知域 (Notification BC)
    └── 职责: 消息推送、邮件通知、系统告警
```

### 领域事件驱动模型
```
用户注册 → UserRegisteredEvent → 创建免费订阅
订阅升级 → SubscriptionUpgradedEvent → 更新所有域的配额
小红书账号失效 → AccountInvalidatedEvent → 暂停相关工作流
代理失效 → ProxyFailedEvent → 触发代理替换流程
配额耗尽 → QuotaExceededEvent → 限制功能访问
```

## 🏛️ 架构分层设计

```
workflow-platform/
├── shared_kernel/                    # 共享内核
│   ├── domain/
│   │   ├── base_entity.py           # 聚合根基类
│   │   ├── value_objects.py         # 共享值对象
│   │   ├── domain_events.py         # 领域事件基类
│   │   └── specifications.py       # 业务规则规约
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── async_session.py    # 异步数据库会话
│   │   │   └── unit_of_work.py     # 工作单元模式
│   │   ├── events/
│   │   │   ├── event_bus.py        # 内存事件总线
│   │   │   └── prefect_publisher.py # Prefect事件发布器
│   │   └── cache/
│   │       └── redis_cache.py      # Redis缓存抽象
│   └── application/
│       ├── commands.py              # CQRS命令基类
│       ├── queries.py               # CQRS查询基类
│       └── handlers.py              # 处理器基类
├── bounded_contexts/                 # 限界上下文
│   ├── user_management/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   └── user.py         # 用户聚合根
│   │   │   ├── value_objects/
│   │   │   │   ├── email.py        # 邮箱值对象
│   │   │   │   └── user_role.py    # 用户角色
│   │   │   ├── repositories/
│   │   │   │   └── user_repository.py
│   │   │   ├── services/
│   │   │   │   ├── authentication_service.py
│   │   │   │   └── password_service.py
│   │   │   └── events/
│   │   │       ├── user_registered.py
│   │   │       └── user_logged_in.py
│   │   ├── application/
│   │   │   ├── commands/
│   │   │   │   ├── register_user.py
│   │   │   │   └── authenticate_user.py
│   │   │   ├── handlers/
│   │   │   │   └── user_command_handlers.py
│   │   │   └── services/
│   │   │       └── user_application_service.py
│   │   ├── infrastructure/
│   │   │   ├── repositories/
│   │   │   │   └── sqlalchemy_user_repository.py
│   │   │   └── auth/
│   │   │       ├── jwt_service.py
│   │   │       └── bcrypt_service.py
│   │   └── presentation/
│   │       ├── api/
│   │       │   └── user_routes.py
│   │       └── schemas/
│   │           └── user_schemas.py
│   ├── subscription/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   ├── subscription.py     # 订阅聚合根
│   │   │   │   ├── plan.py            # 套餐实体
│   │   │   │   └── payment_order.py   # 支付订单
│   │   │   ├── value_objects/
│   │   │   │   ├── money.py           # 金钱值对象
│   │   │   │   ├── billing_cycle.py   # 计费周期
│   │   │   │   └── feature_quota.py   # 功能配额
│   │   │   ├── services/
│   │   │   │   ├── pricing_service.py  # 定价服务
│   │   │   │   ├── quota_service.py    # 配额管理
│   │   │   │   └── payment_service.py  # 支付处理
│   │   │   └── events/
│   │   │       ├── subscription_created.py
│   │   │       ├── subscription_upgraded.py
│   │   │       └── payment_completed.py
│   │   ├── application/
│   │   │   ├── commands/
│   │   │   │   ├── create_subscription.py
│   │   │   │   ├── upgrade_subscription.py
│   │   │   │   └── process_payment.py
│   │   │   └── services/
│   │   │       ├── subscription_service.py
│   │   │       └── billing_service.py
│   │   ├── infrastructure/
│   │   │   ├── repositories/
│   │   │   │   ├── subscription_repository.py
│   │   │   │   └── payment_repository.py
│   │   │   └── payment/
│   │   │       ├── alipay_client.py
│   │   │       └── wechat_client.py
│   │   └── presentation/
│   │       └── api/
│   │           ├── subscription_routes.py
│   │           └── payment_routes.py
│   ├── xiaohongshu/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   ├── xiaohongshu_account.py  # 小红书账号聚合根
│   │   │   │   ├── content.py             # 内容实体
│   │   │   │   └── message.py             # 私信实体
│   │   │   ├── value_objects/
│   │   │   │   ├── account_credentials.py
│   │   │   │   ├── account_health.py
│   │   │   │   └── content_metrics.py
│   │   │   ├── services/
│   │   │   │   ├── account_validation_service.py
│   │   │   │   ├── content_extraction_service.py
│   │   │   │   └── messaging_service.py
│   │   │   └── events/
│   │   │       ├── account_created.py
│   │   │       ├── account_invalidated.py
│   │   │       └── content_collected.py
│   │   ├── application/
│   │   │   ├── commands/
│   │   │   │   ├── create_account.py
│   │   │   │   ├── collect_content.py
│   │   │   │   └── send_message.py
│   │   │   └── services/
│   │   │       ├── xiaohongshu_service.py
│   │   │       └── content_service.py
│   │   ├── infrastructure/
│   │   │   ├── repositories/
│   │   │   │   └── xiaohongshu_repository.py
│   │   │   └── external/
│   │   │       ├── xiaohongshu_api_client.py
│   │   │       └── content_parser.py
│   │   └── presentation/
│   │       └── api/
│   │           └── xiaohongshu_routes.py
│   ├── qidian/                      # 类似结构
│   ├── proxy_pool/                  # 类似结构
│   └── workflow/                    # 类似结构
├── event_driven_coordination/       # 事件驱动协调层
│   ├── event_handlers/
│   │   ├── subscription_event_handlers.py
│   │   ├── user_event_handlers.py
│   │   └── system_event_handlers.py
│   ├── workflows/                   # Prefect工作流定义
│   │   ├── user_onboarding_flow.py
│   │   ├── subscription_lifecycle_flow.py
│   │   ├── xiaohongshu_automation_flow.py
│   │   ├── qidian_scraping_flow.py
│   │   ├── proxy_health_monitoring_flow.py
│   │   └── system_maintenance_flow.py
│   └── automations/                 # Prefect自动化配置
│       ├── quota_monitoring.py
│       ├── payment_processing.py
│       └── system_alerts.py
├── api_gateway/                     # API网关层
│   ├── main.py                      # FastAPI主应用
│   ├── middleware/
│   │   ├── authentication.py       # JWT认证中间件
│   │   ├── authorization.py        # 权限检查中间件
│   │   ├── quota_enforcement.py    # 配额强制中间件
│   │   └── rate_limiting.py        # 频率限制中间件
│   ├── dependencies/
│   │   ├── auth_dependencies.py    # 认证依赖
│   │   ├── permission_dependencies.py # 权限依赖
│   │   └── quota_dependencies.py   # 配额检查依赖
│   └── routers/
│       ├── auth_router.py
│       ├── user_router.py
│       ├── subscription_router.py
│       ├── xiaohongshu_router.py
│       ├── qidian_router.py
│       └── workflow_router.py
├── container.py                     # 依赖注入容器配置
├── config/
│   ├── settings.py                  # 应用配置
│   ├── database.py                  # 数据库配置
│   └── prefect_config.py           # Prefect配置
└── migrations/                      # 数据库迁移
    └── alembic/
```

## 💰 阶梯式服务计费模型

### 小红书服务计费
```python
XIAOHONGSHU_SERVICE_PLANS = {
    "xiaohongshu_free": {
        "service_type": "xiaohongshu",
        "name": "小红书免费版",
        "price_monthly": 0,
        "features": {
            "account_limit": 1,                    # 1个小红书账号
            "daily_api_calls": 50,                 # 每日50次API调用
            "content_collection": True,            # 基础内容采集
            "private_messaging": False,            # 不支持私信
            "data_analytics": False,               # 不支持数据分析
            "export_formats": ["json"],            # 只支持JSON导出
            "data_retention_days": 7,              # 7天数据保留
            "automation_workflows": 1,             # 1个自动化工作流
        }
    },
    "xiaohongshu_basic": {
        "service_type": "xiaohongshu", 
        "name": "小红书基础版",
        "price_monthly": 39.9,
        "features": {
            "account_limit": 5,                    # 5个小红书账号
            "daily_api_calls": 500,                # 每日500次API调用
            "content_collection": True,            # 内容采集
            "private_messaging": True,             # 支持私信功能
            "data_analytics": False,               # 基础统计
            "export_formats": ["json", "excel"],   # JSON+Excel导出
            "data_retention_days": 30,             # 30天数据保留
            "automation_workflows": 3,             # 3个自动化工作流
            "advanced_filters": True,              # 高级筛选
        }
    },
    "xiaohongshu_pro": {
        "service_type": "xiaohongshu",
        "name": "小红书专业版", 
        "price_monthly": 129.9,
        "features": {
            "account_limit": 20,                   # 20个小红书账号
            "daily_api_calls": 5000,               # 每日5000次API调用
            "content_collection": True,            # 高级内容采集
            "private_messaging": True,             # 智能私信管理
            "data_analytics": True,                # 完整数据分析
            "export_formats": ["json", "excel", "pdf"], # 全格式导出
            "data_retention_days": 90,             # 90天数据保留
            "automation_workflows": 10,            # 10个自动化工作流
            "advanced_filters": True,              # 高级筛选
            "ai_insights": True,                   # AI洞察分析
            "batch_operations": True,              # 批量操作
        }
    },
    "xiaohongshu_enterprise": {
        "service_type": "xiaohongshu",
        "name": "小红书企业版",
        "price_monthly": 399.9,
        "features": {
            "account_limit": -1,                   # 无限制账号
            "daily_api_calls": -1,                 # 无限制API调用
            "content_collection": True,            # 企业级内容采集
            "private_messaging": True,             # 企业级私信管理
            "data_analytics": True,                # 企业级分析
            "export_formats": ["json", "excel", "pdf", "api"], # 全格式+API
            "data_retention_days": 365,            # 365天数据保留
            "automation_workflows": -1,            # 无限制工作流
            "advanced_filters": True,              # 高级筛选
            "ai_insights": True,                   # AI洞察分析
            "batch_operations": True,              # 批量操作
            "custom_integration": True,            # 定制集成
            "dedicated_support": True,             # 专属客服
        }
    }
}
```

### 起点服务计费
```python
QIDIAN_SERVICE_PLANS = {
    "qidian_free": {
        "service_type": "qidian",
        "name": "起点免费版",
        "price_monthly": 0,
        "features": {
            "novel_tracking_limit": 10,           # 监控10本小说
            "ranking_access": ["热销榜"],          # 只能访问热销榜
            "data_collection_frequency": "daily", # 每日采集
            "author_info": False,                  # 不支持作者信息
            "trend_analysis": False,               # 不支持趋势分析
            "export_formats": ["json"],            # 只支持JSON
            "data_retention_days": 7,              # 7天数据保留
            "alert_notifications": 1,              # 1个提醒通知
        }
    },
    "qidian_basic": {
        "service_type": "qidian",
        "name": "起点基础版",
        "price_monthly": 29.9,
        "features": {
            "novel_tracking_limit": 100,          # 监控100本小说
            "ranking_access": ["热销榜", "收藏榜", "推荐榜"], # 多个榜单
            "data_collection_frequency": "hourly", # 每小时采集
            "author_info": True,                   # 支持作者信息
            "trend_analysis": False,               # 基础趋势
            "export_formats": ["json", "excel"],   # JSON+Excel
            "data_retention_days": 30,             # 30天数据保留
            "alert_notifications": 5,              # 5个提醒通知
            "custom_keywords": True,               # 自定义关键词监控
        }
    },
    "qidian_pro": {
        "service_type": "qidian",
        "name": "起点专业版",
        "price_monthly": 89.9, 
        "features": {
            "novel_tracking_limit": 1000,         # 监控1000本小说
            "ranking_access": "all",               # 所有榜单
            "data_collection_frequency": "realtime", # 实时采集
            "author_info": True,                   # 完整作者信息
            "trend_analysis": True,                # 高级趋势分析
            "export_formats": ["json", "excel", "pdf"], # 全格式
            "data_retention_days": 90,             # 90天数据保留
            "alert_notifications": 20,             # 20个提醒通知
            "custom_keywords": True,               # 自定义关键词
            "competitor_analysis": True,           # 竞品分析
            "market_insights": True,               # 市场洞察
        }
    },
    "qidian_enterprise": {
        "service_type": "qidian",
        "name": "起点企业版",
        "price_monthly": 299.9,
        "features": {
            "novel_tracking_limit": -1,           # 无限制
            "ranking_access": "all",               # 所有榜单
            "data_collection_frequency": "realtime", # 实时采集
            "author_info": True,                   # 企业级作者档案
            "trend_analysis": True,                # 企业级趋势分析
            "export_formats": ["json", "excel", "pdf", "api"], # 全格式+API
            "data_retention_days": 365,            # 365天数据保留
            "alert_notifications": -1,             # 无限制通知
            "custom_keywords": True,               # 自定义关键词
            "competitor_analysis": True,           # 竞品分析
            "market_insights": True,               # 市场洞察
            "custom_reports": True,                # 定制报告
            "api_access": True,                    # API访问
        }
    }
}
```

## 📊 数据库设计

### 核心表结构设计

#### 用户管理相关表
```sql
-- 用户基础表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'banned')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- 用户Profile表
CREATE TABLE user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'UTC',
    notification_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户会话表
CREATE TABLE user_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 服务订阅相关表
```sql
-- 服务类型枚举表
CREATE TABLE service_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL, -- xiaohongshu, qidian, douyin, etc.
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 服务套餐表
CREATE TABLE service_plans (
    id BIGSERIAL PRIMARY KEY,
    service_type_id INTEGER REFERENCES service_types(id),
    plan_code VARCHAR(50) NOT NULL, -- free, basic, pro, enterprise
    plan_name VARCHAR(100) NOT NULL,
    price_monthly DECIMAL(10,2) NOT NULL DEFAULT 0,
    price_yearly DECIMAL(10,2),
    billing_cycle_months INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(service_type_id, plan_code)
);

-- 套餐功能配置表
CREATE TABLE plan_features (
    id BIGSERIAL PRIMARY KEY,
    plan_id BIGINT REFERENCES service_plans(id) ON DELETE CASCADE,
    feature_key VARCHAR(100) NOT NULL, -- account_limit, daily_api_calls, etc.
    feature_value INTEGER, -- -1表示无限制, NULL表示不支持
    is_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(plan_id, feature_key)
);

-- 用户服务订阅表
CREATE TABLE user_service_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    service_type_id INTEGER REFERENCES service_types(id),
    plan_id BIGINT REFERENCES service_plans(id),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'expired', 'cancelled', 'suspended')),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    auto_renew BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, service_type_id) -- 一个用户每个服务只能有一个活跃订阅
);

-- 功能使用量统计表
CREATE TABLE feature_usage_stats (
    id BIGSERIAL PRIMARY KEY,
    subscription_id BIGINT REFERENCES user_service_subscriptions(id),
    feature_key VARCHAR(100) NOT NULL,
    usage_date DATE NOT NULL,
    usage_count INTEGER DEFAULT 0,
    quota_limit INTEGER, -- 当日配额限制
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(subscription_id, feature_key, usage_date)
);
```

#### 支付订单相关表
```sql
-- 支付订单表
CREATE TABLE payment_orders (
    id VARCHAR(64) PRIMARY KEY, -- 自定义订单号
    user_id BIGINT REFERENCES users(id),
    subscription_id BIGINT REFERENCES user_service_subscriptions(id),
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('new_subscription', 'renewal', 'upgrade')),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    payment_method VARCHAR(20) CHECK (payment_method IN ('alipay', 'wechat', 'bank_card')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed', 'refunded', 'cancelled')),
    external_order_id VARCHAR(255), -- 第三方支付订单号
    payment_url TEXT, -- 支付链接
    paid_at TIMESTAMP WITH TIME ZONE,
    expired_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 支付回调日志表
CREATE TABLE payment_callbacks (
    id BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(64) REFERENCES payment_orders(id),
    payment_method VARCHAR(20),
    callback_data JSONB,
    is_verified BOOLEAN,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 小红书服务相关表
```sql
-- 小红书账号表
CREATE TABLE xiaohongshu_accounts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    username VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    account_type VARCHAR(20) DEFAULT 'personal' CHECK (account_type IN ('personal', 'business')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'invalid', 'banned', 'suspended')),
    cookies TEXT, -- 加密存储
    session_info JSONB, -- 会话信息
    health_score INTEGER DEFAULT 100 CHECK (health_score >= 0 AND health_score <= 100),
    last_active_at TIMESTAMP WITH TIME ZONE,
    verification_status VARCHAR(20) DEFAULT 'unverified',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 小红书内容采集表
CREATE TABLE xiaohongshu_contents (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT REFERENCES xiaohongshu_accounts(id),
    content_id VARCHAR(100) NOT NULL, -- 小红书内容ID
    content_type VARCHAR(20) CHECK (content_type IN ('note', 'video', 'live')),
    title TEXT,
    content TEXT,
    author_id VARCHAR(100),
    author_name VARCHAR(200),
    publish_time TIMESTAMP WITH TIME ZONE,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    collect_count INTEGER DEFAULT 0,
    images JSONB, -- 图片链接数组
    tags JSONB, -- 标签数组
    location JSONB, -- 位置信息
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(account_id, content_id)
);

-- 小红书私信表
CREATE TABLE xiaohongshu_messages (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT REFERENCES xiaohongshu_accounts(id),
    conversation_id VARCHAR(100),
    message_id VARCHAR(100),
    direction VARCHAR(10) CHECK (direction IN ('sent', 'received')),
    content TEXT,
    message_type VARCHAR(20) DEFAULT 'text',
    target_user_id VARCHAR(100),
    target_username VARCHAR(200),
    sent_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'sent',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 起点服务相关表
```sql
-- 起点小说监控表
CREATE TABLE qidian_novel_trackings (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    novel_id VARCHAR(100) NOT NULL,
    novel_name VARCHAR(500) NOT NULL,
    author_name VARCHAR(200),
    category VARCHAR(100),
    status VARCHAR(20) CHECK (status IN ('active', 'paused', 'completed', 'dropped')),
    tracking_frequency VARCHAR(20) DEFAULT 'daily', -- hourly, daily, weekly
    last_check_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, novel_id)
);

-- 起点小说数据表
CREATE TABLE qidian_novel_data (
    id BIGSERIAL PRIMARY KEY,
    tracking_id BIGINT REFERENCES qidian_novel_trackings(id),
    novel_id VARCHAR(100),
    ranking_data JSONB, -- 各种榜单排名
    stats_data JSONB, -- 点击、推荐、收藏等数据
    chapter_count INTEGER,
    word_count BIGINT,
    update_status VARCHAR(50),
    last_update_time TIMESTAMP WITH TIME ZONE,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 起点榜单数据表
CREATE TABLE qidian_rankings (
    id BIGSERIAL PRIMARY KEY,
    ranking_type VARCHAR(50) NOT NULL, -- 热销榜、收藏榜等
    novel_id VARCHAR(100) NOT NULL,
    novel_name VARCHAR(500),
    author_name VARCHAR(200),
    rank_position INTEGER,
    rank_score BIGINT,
    category VARCHAR(100),
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ranking_date DATE NOT NULL,
    UNIQUE(ranking_type, novel_id, ranking_date)
);
```

#### 代理池相关表
```sql
-- 代理池表
CREATE TABLE proxy_pool (
    id BIGSERIAL PRIMARY KEY,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    protocol VARCHAR(10) DEFAULT 'http' CHECK (protocol IN ('http', 'https', 'socks5')),
    username VARCHAR(255),
    password VARCHAR(255),
    country_code VARCHAR(3),
    region VARCHAR(100),
    provider VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'failed', 'banned')),
    success_rate DECIMAL(5,2) DEFAULT 100.00,
    avg_response_time INTEGER, -- 平均响应时间(ms)
    last_check_at TIMESTAMP WITH TIME ZONE,
    last_success_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(host, port, username)
);

-- 代理使用记录表
CREATE TABLE proxy_usage_logs (
    id BIGSERIAL PRIMARY KEY,
    proxy_id BIGINT REFERENCES proxy_pool(id),
    user_id BIGINT REFERENCES users(id),
    service_type VARCHAR(50),
    request_url TEXT,
    response_status INTEGER,
    response_time INTEGER,
    success BOOLEAN,
    error_message TEXT,
    used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 工作流相关表
```sql
-- 工作流定义表
CREATE TABLE workflow_definitions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    service_type VARCHAR(50) NOT NULL,
    workflow_name VARCHAR(200) NOT NULL,
    workflow_type VARCHAR(50), -- data_collection, automation, monitoring
    config JSONB NOT NULL, -- 工作流配置
    schedule_config JSONB, -- 调度配置
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'disabled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 工作流执行记录表
CREATE TABLE workflow_executions (
    id BIGSERIAL PRIMARY KEY,
    workflow_id BIGINT REFERENCES workflow_definitions(id),
    prefect_flow_run_id VARCHAR(255), -- Prefect流程运行ID
    status VARCHAR(20) CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    execution_log JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 数据库索引设计
```sql
-- 用户相关索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);

-- 订阅相关索引
CREATE INDEX idx_subscriptions_user_id ON user_service_subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON user_service_subscriptions(status);
CREATE INDEX idx_subscriptions_expires ON user_service_subscriptions(expires_at);
CREATE INDEX idx_feature_usage_date ON feature_usage_stats(usage_date);
CREATE INDEX idx_feature_usage_subscription ON feature_usage_stats(subscription_id, feature_key, usage_date);

-- 支付相关索引
CREATE INDEX idx_payment_orders_user ON payment_orders(user_id);
CREATE INDEX idx_payment_orders_status ON payment_orders(status);
CREATE INDEX idx_payment_orders_created ON payment_orders(created_at);

-- 业务数据索引
CREATE INDEX idx_xiaohongshu_accounts_user ON xiaohongshu_accounts(user_id);
CREATE INDEX idx_xiaohongshu_contents_account ON xiaohongshu_contents(account_id);
CREATE INDEX idx_xiaohongshu_contents_collected ON xiaohongshu_contents(collected_at);
CREATE INDEX idx_qidian_trackings_user ON qidian_novel_trackings(user_id);
CREATE INDEX idx_qidian_data_collected ON qidian_novel_data(collected_at);
CREATE INDEX idx_proxy_pool_status ON proxy_pool(status);
CREATE INDEX idx_proxy_usage_user_service ON proxy_usage_logs(user_id, service_type);
```

## 🔌 API设计规范

### RESTful API 端点设计

#### 认证和用户管理API
```python
# 认证相关
POST   /api/v1/auth/register          # 用户注册
POST   /api/v1/auth/login             # 用户登录
POST   /api/v1/auth/logout            # 用户登出
POST   /api/v1/auth/refresh           # 刷新Token
POST   /api/v1/auth/forgot-password   # 忘记密码
POST   /api/v1/auth/reset-password    # 重置密码

# 用户管理
GET    /api/v1/users/profile          # 获取用户资料
PUT    /api/v1/users/profile          # 更新用户资料
GET    /api/v1/users/sessions         # 获取用户会话列表
DELETE /api/v1/users/sessions/{id}    # 删除特定会话
```

#### 订阅管理API
```python
# 服务和套餐查询
GET    /api/v1/services               # 获取所有可用服务
GET    /api/v1/services/{service_type}/plans  # 获取特定服务的套餐

# 用户订阅管理
GET    /api/v1/subscriptions          # 获取用户所有订阅
POST   /api/v1/subscriptions          # 创建新订阅
PUT    /api/v1/subscriptions/{id}     # 升级/修改订阅
DELETE /api/v1/subscriptions/{id}     # 取消订阅
GET    /api/v1/subscriptions/{id}/usage  # 获取订阅使用情况

# 支付相关
POST   /api/v1/payments/orders        # 创建支付订单
GET    /api/v1/payments/orders/{id}   # 获取订单状态
POST   /api/v1/payments/callback/alipay    # 支付宝回调
POST   /api/v1/payments/callback/wechat    # 微信支付回调
```

#### 小红书服务API
```python
# 账号管理
GET    /api/v1/xiaohongshu/accounts         # 获取用户的小红书账号列表
POST   /api/v1/xiaohongshu/accounts         # 添加小红书账号
PUT    /api/v1/xiaohongshu/accounts/{id}    # 更新账号信息
DELETE /api/v1/xiaohongshu/accounts/{id}    # 删除账号
POST   /api/v1/xiaohongshu/accounts/{id}/verify  # 验证账号

# 内容采集
GET    /api/v1/xiaohongshu/contents          # 获取采集的内容列表
POST   /api/v1/xiaohongshu/contents/collect  # 手动触发内容采集
GET    /api/v1/xiaohongshu/contents/{id}     # 获取特定内容详情
DELETE /api/v1/xiaohongshu/contents/{id}     # 删除内容

# 私信管理
GET    /api/v1/xiaohongshu/messages          # 获取私信列表
POST   /api/v1/xiaohongshu/messages          # 发送私信
GET    /api/v1/xiaohongshu/conversations     # 获取对话列表

# 数据分析
GET    /api/v1/xiaohongshu/analytics/overview    # 获取数据概览
GET    /api/v1/xiaohongshu/analytics/trends      # 获取趋势分析
GET    /api/v1/xiaohongshu/analytics/export      # 导出数据报告
```

#### 起点服务API
```python
# 小说监控管理
GET    /api/v1/qidian/trackings         # 获取监控的小说列表
POST   /api/v1/qidian/trackings         # 添加小说监控
PUT    /api/v1/qidian/trackings/{id}    # 更新监控设置
DELETE /api/v1/qidian/trackings/{id}    # 删除监控

# 小说数据
GET    /api/v1/qidian/novels/{id}/data  # 获取小说数据历史
GET    /api/v1/qidian/novels/{id}/trends # 获取小说趋势分析

# 榜单数据
GET    /api/v1/qidian/rankings          # 获取榜单数据
GET    /api/v1/qidian/rankings/{type}   # 获取特定类型榜单

# 数据分析
GET    /api/v1/qidian/analytics/market  # 获取市场分析
GET    /api/v1/qidian/analytics/author/{author}  # 获取作者分析
```

#### 工作流管理API
```python
# 工作流定义
GET    /api/v1/workflows               # 获取用户工作流列表
POST   /api/v1/workflows               # 创建新工作流
PUT    /api/v1/workflows/{id}          # 更新工作流
DELETE /api/v1/workflows/{id}          # 删除工作流

# 工作流执行
POST   /api/v1/workflows/{id}/execute  # 手动执行工作流
GET    /api/v1/workflows/{id}/executions  # 获取执行历史
GET    /api/v1/workflows/executions/{id}   # 获取执行详情
POST   /api/v1/workflows/executions/{id}/cancel  # 取消执行
```

### API响应格式标准
```python
# 成功响应格式
{
    "success": true,
    "data": {...},
    "message": "操作成功",
    "timestamp": "2024-01-01T12:00:00Z"
}

# 错误响应格式
{
    "success": false,
    "error": {
        "code": "PERMISSION_DENIED",
        "message": "权限不足",
        "details": {...}
    },
    "timestamp": "2024-01-01T12:00:00Z"
}

# 分页响应格式
{
    "success": true,
    "data": {
        "items": [...],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 100,
            "total_pages": 5,
            "has_next": true,
            "has_prev": false
        }
    }
}
```

## 🚀 详细实施计划

### Phase 1: 基础架构搭建 (Week 1-2)

#### Week 1: 项目初始化
**后端任务**:
- [ ] 创建DDD分层项目结构
- [ ] 配置Docker开发环境(PostgreSQL, Redis)
- [ ] 建立SQLAlchemy模型和迁移系统
- [ ] 实现依赖注入容器配置
- [ ] 建立基础的认证和授权系统

**前端任务**:
- [ ] 创建React/Vue项目结构
- [ ] 配置路由和状态管理
- [ ] 实现基础布局组件
- [ ] 集成HTTP客户端和拦截器
- [ ] 建立主题和样式系统

**数据库任务**:
- [ ] 创建用户管理相关表
- [ ] 创建服务订阅相关表
- [ ] 创建支付订单相关表
- [ ] 建立基础索引和约束
- [ ] 准备测试数据

#### Week 2: 认证系统
**后端任务**:
- [ ] 实现JWT认证服务
- [ ] 实现用户注册/登录API
- [ ] 实现密码重置功能
- [ ] 建立权限检查中间件
- [ ] 实现会话管理

**前端任务**:
- [ ] 实现登录/注册页面
- [ ] 实现密码重置流程
- [ ] 建立认证状态管理
- [ ] 实现路由守卫
- [ ] 实现用户菜单组件

### Phase 2: 订阅系统开发 (Week 3-4)

#### Week 3: 订阅管理
**后端任务**:
- [ ] 实现订阅领域模型和仓储
- [ ] 实现套餐配置系统
- [ ] 实现订阅创建和升级逻辑
- [ ] 实现配额管理服务
- [ ] 建立权限检查装饰器

**前端任务**:
- [ ] 实现订阅概览页面
- [ ] 实现套餐选择组件
- [ ] 实现使用量展示组件
- [ ] 实现订阅管理页面
- [ ] 建立订阅状态展示

#### Week 4: 支付集成
**后端任务**:
- [ ] 集成支付宝SDK
- [ ] 集成微信支付SDK
- [ ] 实现支付订单管理
- [ ] 实现支付回调处理
- [ ] 建立支付状态查询

**前端任务**:
- [ ] 实现支付流程页面
- [ ] 实现支付方式选择
- [ ] 实现支付状态查询
- [ ] 实现账单历史页面
- [ ] 建立支付结果展示

### Phase 3: 代理池系统 (Week 5)

**后端任务**:
- [ ] 实现代理池领域模型
- [ ] 实现代理健康检查机制
- [ ] 实现智能代理分配算法
- [ ] 建立代理使用量统计
- [ ] 实现代理轮换策略

**前端任务**:
- [ ] 实现代理池状态监控页面
- [ ] 实现代理配置管理
- [ ] 建立代理使用统计图表
- [ ] 实现代理测试功能

### Phase 4: 小红书服务开发 (Week 6-7)

#### Week 6: 账号管理
**后端任务**:
- [ ] 实现小红书账号领域模型
- [ ] 实现账号验证和健康检查
- [ ] 集成小红书API客户端
- [ ] 实现账号管理API
- [ ] 建立账号监控工作流

**前端任务**:
- [ ] 实现小红书账号管理页面
- [ ] 实现账号添加表单
- [ ] 实现账号状态监控
- [ ] 建立账号健康度展示
- [ ] 实现账号批量操作

#### Week 7: 内容采集和私信
**后端任务**:
- [ ] 实现内容采集功能
- [ ] 实现私信管理功能
- [ ] 建立数据分析服务
- [ ] 实现数据导出功能
- [ ] 建立内容采集工作流

**前端任务**:
- [ ] 实现内容展示页面
- [ ] 实现内容筛选和搜索
- [ ] 实现私信管理界面
- [ ] 建立数据分析图表
- [ ] 实现数据导出功能

### Phase 5: 起点服务开发 (Week 8)

**后端任务**:
- [ ] 实现起点爬虫系统
- [ ] 实现小说监控功能
- [ ] 实现榜单数据采集
- [ ] 建立市场分析服务
- [ ] 实现数据监控工作流

**前端任务**:
- [ ] 实现小说监控管理页面
- [ ] 实现榜单数据展示
- [ ] 建立市场分析图表
- [ ] 实现监控配置界面
- [ ] 建立趋势分析展示

### Phase 6: 工作流系统集成 (Week 9)

**后端任务**:
- [ ] 集成Prefect工作流引擎
- [ ] 实现事件驱动工作流
- [ ] 建立工作流调度系统
- [ ] 实现工作流监控
- [ ] 建立自动化规则引擎

**前端任务**:
- [ ] 实现工作流管理页面
- [ ] 建立工作流可视化编辑器
- [ ] 实现执行历史查看
- [ ] 建立工作流监控面板
- [ ] 实现调度配置界面

### Phase 7: 系统集成和测试 (Week 10-12)

#### Week 10-11: 集成测试
- [ ] 端到端功能测试
- [ ] 支付流程测试
- [ ] 工作流稳定性测试
- [ ] 性能压力测试
- [ ] 安全渗透测试

#### Week 12: 生产部署
- [ ] 生产环境配置
- [ ] 监控告警系统
- [ ] 日志收集系统
- [ ] 备份恢复策略
- [ ] 发布和运维文档

## 📝 开发规范和最佳实践

### 代码质量标准
- Python代码遵循PEP 8规范
- 使用Type Hints进行类型注解
- 单元测试覆盖率不低于80%
- 集成测试覆盖主要业务流程
- 使用pre-commit hooks进行代码质量检查

### Git工作流规范
- 使用Git Flow分支模型
- feature/* 分支开发新功能
- develop分支用于集成测试
- main分支用于生产发布
- 每个PR必须经过代码审查

### 部署和运维
- 使用Docker容器化部署
- Kubernetes进行容器编排
- CI/CD自动化部署流水线
- 完整的监控和告警体系
- 定期的安全漏洞扫描

这个详细的设计方案为前端、后端和数据库开发提供了完整的指导，每个阶段都有明确的交付物和验收标准，确保项目能够按计划高质量交付。