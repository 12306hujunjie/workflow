# Workflow Platform API 和部署指南

## 📋 项目概述

**Workflow Platform** 是一个基于DDD（领域驱动设计）+ 事件驱动架构的SaaS自动化工作流平台，支持多平台数据采集、用户订阅计费、智能代理池管理等功能。

### 核心特性
- 🔐 完整的用户认证授权系统（JWT + 邮箱验证码）
- 🏗️ 基于DDD的模块化架构设计
- 🚀 事件驱动的异步处理机制
- 📊 多平台数据采集（小红书、起点等）
- 💰 灵活的订阅计费模型
- 🔄 智能代理池管理
- 📱 现代化的React前端界面

## 🏛️ 系统架构

### 技术栈

**后端技术栈：**
- **框架**: FastAPI 0.104+ (异步Web框架)
- **ORM**: SQLAlchemy 2.0 (异步ORM)
- **数据验证**: Pydantic v2 (Rust内核性能)
- **依赖注入**: Dependency Injector (企业级DI容器)
- **工作流引擎**: Prefect 3.0 (事件驱动工作流编排)
- **数据库**: PostgreSQL 15+ (主数据库)
- **缓存**: Redis 7+ (缓存、会话、消息队列)
- **认证**: JWT (JSON Web Token)
- **容器化**: Docker + Docker Compose

**前端技术栈：**
- **框架**: React 19.1.0 + TypeScript
- **构建工具**: Vite 7.0.4
- **UI组件库**: Ant Design 5.26.6
- **样式框架**: Tailwind CSS 4.1.11
- **状态管理**: Zustand 5.0.6
- **路由**: React Router DOM 7.7.1
- **HTTP客户端**: Axios 1.11.0
- **日期处理**: Day.js 1.11.13

### 架构设计原则

1. **领域驱动设计 (DDD)**
   - 限界上下文隔离：每个 `bounded_contexts` 下的模块保持独立
   - 共享内核：公共功能放在 `shared_kernel` 中
   - 依赖方向：API → Application → Domain → Infrastructure

2. **事件驱动架构**
   - 跨上下文通信通过 `event_driven_coordination`
   - 异步事件处理提高系统响应性
   - 松耦合的模块间通信

3. **分层架构**
   ```
   ┌─────────────────────────────────────┐
   │           API Gateway               │  ← 统一入口、认证、限流
   ├─────────────────────────────────────┤
   │        Bounded Contexts             │  ← 业务领域模块
   │  ┌─────────┬─────────┬─────────┐    │
   │  │ User    │ Workflow│ Proxy   │    │
   │  │ Mgmt    │ Engine  │ Pool    │    │
   │  └─────────┴─────────┴─────────┘    │
   ├─────────────────────────────────────┤
   │      Event Driven Coordination      │  ← 事件协调层
   ├─────────────────────────────────────┤
   │          Shared Kernel              │  ← 共享基础设施
   └─────────────────────────────────────┘
   ```

## 🗂️ 项目结构

```
workflow/
├── frontend/                     # React前端应用
│   ├── src/
│   │   ├── components/           # 可复用组件
│   │   ├── pages/               # 页面组件
│   │   ├── hooks/               # 自定义Hooks
│   │   ├── services/            # API服务
│   │   ├── store/               # Zustand状态管理
│   │   ├── types/               # TypeScript类型定义
│   │   ├── utils/               # 工具函数
│   │   └── router/              # 路由配置
│   ├── package.json
│   └── vite.config.ts
├── workflow-platform/            # Python后端应用
│   ├── api_gateway/             # API网关层
│   │   ├── main.py             # FastAPI主应用
│   │   ├── middleware/         # 中间件（认证、限流等）
│   │   └── routers/            # 路由聚合器
│   ├── bounded_contexts/        # 限界上下文
│   │   ├── user_management/    # 用户管理域
│   │   ├── subscription/       # 订阅计费域
│   │   ├── workflow/           # 工作流域
│   │   ├── proxy_pool/         # 代理池域
│   │   ├── xiaohongshu/        # 小红书域
│   │   └── qidian/             # 起点域
│   ├── shared_kernel/           # 共享内核
│   │   ├── domain/             # 共享领域模型
│   │   ├── application/        # 共享应用服务
│   │   └── infrastructure/     # 共享基础设施
│   ├── event_driven_coordination/ # 事件驱动协调
│   │   ├── event_handlers/     # 事件处理器
│   │   ├── workflows/          # Prefect工作流
│   │   └── automations/        # 自动化配置
│   ├── config/                 # 配置文件
│   ├── container.py            # 依赖注入容器
│   ├── requirements.txt        # Python依赖
│   ├── Dockerfile              # Docker镜像构建
│   └── docker-compose.yml      # 容器编排
├── docs/                       # 项目文档
└── .github/workflows/          # CI/CD配置
```

## 🔌 API 架构设计

### API 网关层

**主入口**: `api_gateway/main.py`
- 统一的API入口点
- 全局中间件配置（CORS、认证、限流）
- 统一异常处理
- 健康检查端点

**路由聚合**: `api_gateway/routers/main_router.py`
```python
def create_api_router(api_prefix: str = "/api/v1") -> APIRouter:
    router = APIRouter(prefix=api_prefix)
    
    # 用户管理上下文
    router.include_router(
        create_user_management_router(),
        tags=["User Management"]
    )
    
    # 工作流执行上下文
    router.include_router(
        create_workflow_execution_router(),
        tags=["Workflow Execution"]
    )
    
    # 其他上下文...
    return router
```

### API 端点结构

**Base URL**: `http://localhost:8001/api/v1`

#### 1. 用户管理 API (`/users`)

**公开认证端点** (`/users/public`):
- `POST /users/public/send-verification-code` - 发送验证码（无需认证）
- `POST /users/public/logout` - 公开登出端点

**认证相关** (`/users/auth`):
- `POST /users/auth/register` - 用户注册（需验证码）
- `POST /users/auth/login` - 用户登录
- `POST /users/auth/refresh` - 刷新访问令牌
- `POST /users/auth/logout` - 用户登出
- `POST /users/auth/reset-password` - 重置密码（需验证码）
- `POST /users/auth/send-verification-code` - 发送验证码
- `GET /users/auth/check-username` - 检查用户名可用性
- `GET /users/auth/check-email` - 检查邮箱可用性

**用户信息管理** (`/users`):
- `GET /users/me` - 获取当前用户信息
- `PUT /users/me/profile` - 更新用户资料
- `POST /users/me/change-password` - 修改密码

**管理员功能** (`/users/admin`):
- `GET /users/admin/users` - 获取用户列表
- `PUT /users/admin/users/{user_id}/status` - 更新用户状态
- `DELETE /users/admin/users/{user_id}` - 删除用户

#### 2. 订阅管理 API (`/subscription`)
- `GET /subscription/plans` - 获取订阅套餐列表
- `POST /subscription/subscribe` - 创建订阅
- `GET /subscription/current` - 获取当前订阅信息
- `POST /subscription/upgrade` - 升级订阅
- `POST /subscription/cancel` - 取消订阅
- `GET /subscription/usage` - 获取使用情况

#### 3. 工作流管理 API (`/workflow`)
- `GET /workflow/definitions` - 获取工作流定义列表
- `POST /workflow/definitions` - 创建工作流定义
- `GET /workflow/executions` - 获取工作流执行历史
- `POST /workflow/executions` - 启动工作流执行
- `GET /workflow/executions/{execution_id}` - 获取执行详情
- `POST /workflow/executions/{execution_id}/cancel` - 取消执行

#### 4. 代理池管理 API (`/proxy`)
- `GET /proxy/pools` - 获取代理池列表
- `POST /proxy/pools` - 创建代理池
- `GET /proxy/pools/{pool_id}/status` - 获取代理池状态
- `POST /proxy/pools/{pool_id}/test` - 测试代理池

### API 响应格式

**统一响应格式**:
```json
{
  "success": true,
  "data": {},           // 响应数据
  "message": "操作成功",  // 响应消息
  "request_id": "req_123456789",  // 请求ID
  "timestamp": "2024-01-01T12:00:00Z"  // 时间戳
}
```

**错误响应格式**:
```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "错误描述信息",
  "details": {          // 可选，详细错误信息
    "field": "具体字段错误"
  },
  "request_id": "req_123456789",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 认证与授权

**JWT 令牌机制**:
- **访问令牌**: 有效期30分钟，用于API调用认证
- **刷新令牌**: 有效期7天，用于获取新的访问令牌
- **令牌传递**: `Authorization: Bearer <token>`

**权限控制**:
- 基于角色的访问控制（RBAC）
- 支持用户角色：`user`, `admin`, `super_admin`
- 细粒度的权限检查

**安全特性**:
- 令牌黑名单机制
- 密码强度验证
- 邮箱验证码验证
- API频率限制
- IP地址限制

## 🚀 部署指南

### 环境要求

**系统要求**:
- **操作系统**: Linux (Ubuntu 20.04+) / macOS / Windows
- **Python**: 3.10+
- **Node.js**: 18+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

**硬件要求**:
- **CPU**: 2核心以上
- **内存**: 4GB以上
- **存储**: 20GB以上可用空间
- **网络**: 稳定的互联网连接

### 开发环境部署

#### 1. 克隆项目
```bash
git clone <repository-url>
cd workflow
```

#### 2. 后端环境配置

**创建虚拟环境**:
```bash
cd workflow-platform
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

**安装依赖**:
```bash
pip install -r requirements.txt
```

**环境变量配置**:
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、Redis、邮件等设置
```

**关键环境变量**:
```bash
# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/workflow_platform

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 邮件配置
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USERNAME=your-email@qq.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@qq.com

# API配置
API_HOST=0.0.0.0
API_PORT=8001
CORS_ALLOWED_ORIGINS=["http://localhost:5174"]

# 应用配置
APP_NAME="Workflow Platform"
APP_VERSION="1.0.0"
DEBUG=true
```

#### 3. 前端环境配置

```bash
cd frontend
npm install
```

**环境变量配置**:
```bash
# 创建 .env.local 文件
echo "VITE_API_BASE_URL=http://localhost:8001/api/v1" > .env.local
```

#### 4. 数据库初始化

**使用Docker启动数据库**:
```bash
cd workflow-platform
docker-compose up -d postgres redis
```

**运行数据库迁移**:
```bash
# 等待数据库启动
sleep 10

# 运行迁移
alembic upgrade head
```

#### 5. 启动服务

**启动后端服务**:
```bash
# 在 workflow-platform 目录下
source .venv/bin/activate
python3 -m uvicorn api_gateway.main:app --host 0.0.0.0 --port 8001 --reload
```

**启动前端服务**:
```bash
# 在 frontend 目录下
npm run dev
```

**访问应用**:
- 前端应用: http://localhost:5174
- 后端API: http://localhost:8001
- API文档: http://localhost:8001/api/docs

### 生产环境部署

#### 1. Docker 容器化部署

**构建镜像**:
```bash
# 后端镜像
cd workflow-platform
docker build -t workflow-platform:latest .

# 前端镜像
cd frontend
docker build -t workflow-frontend:latest .
```

**使用 Docker Compose**:
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - workflow-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - workflow-network

  backend:
    image: workflow-platform:latest
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    depends_on:
      - postgres
      - redis
    networks:
      - workflow-network

  frontend:
    image: workflow-frontend:latest
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - workflow-network

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - workflow-network

volumes:
  postgres_data:
  redis_data:

networks:
  workflow-network:
    driver: bridge
```

**启动生产环境**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### 2. Kubernetes 部署

**命名空间**:
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: workflow-platform
```

**ConfigMap**:
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: workflow-config
  namespace: workflow-platform
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  APP_NAME: "Workflow Platform"
  DEBUG: "false"
```

**Secret**:
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: workflow-secrets
  namespace: workflow-platform
type: Opaque
data:
  jwt-secret: <base64-encoded-jwt-secret>
  db-password: <base64-encoded-db-password>
  smtp-password: <base64-encoded-smtp-password>
```

**Deployment**:
```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-backend
  namespace: workflow-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: workflow-backend
  template:
    metadata:
      labels:
        app: workflow-backend
    spec:
      containers:
      - name: backend
        image: workflow-platform:latest
        ports:
        - containerPort: 8000
        env:
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: workflow-secrets
              key: jwt-secret
        envFrom:
        - configMapRef:
            name: workflow-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

**Service**:
```yaml
# backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: workflow-backend-service
  namespace: workflow-platform
spec:
  selector:
    app: workflow-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

**Ingress**:
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: workflow-ingress
  namespace: workflow-platform
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.workflow-platform.com
    secretName: workflow-tls
  rules:
  - host: api.workflow-platform.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: workflow-backend-service
            port:
              number: 8000
```

#### 3. 云服务部署

**AWS ECS 部署**:
```json
{
  "family": "workflow-platform",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "workflow-backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/workflow-platform:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql+asyncpg://user:pass@rds-endpoint:5432/db"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/workflow-platform",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 监控和日志

#### 1. 应用监控

**Prometheus + Grafana**:
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'workflow-platform'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

**健康检查端点**:
```python
# 在 FastAPI 应用中
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "database": await check_database_health(),
        "redis": await check_redis_health()
    }

@app.get("/metrics")
async def metrics():
    # Prometheus metrics endpoint
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

#### 2. 日志管理

**结构化日志配置**:
```python
# config/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        return json.dumps(log_entry)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

**ELK Stack 集成**:
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

### 性能优化

#### 1. 数据库优化

**连接池配置**:
```python
# config/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # 连接池大小
    max_overflow=30,        # 最大溢出连接数
    pool_pre_ping=True,     # 连接前检查
    pool_recycle=3600,      # 连接回收时间（秒）
    echo=False              # 生产环境关闭SQL日志
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

**索引优化**:
```sql
-- 用户表索引
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_users_username ON users(username);
CREATE INDEX CONCURRENTLY idx_users_status ON users(status);
CREATE INDEX CONCURRENTLY idx_users_created_at ON users(created_at);

-- 复合索引
CREATE INDEX CONCURRENTLY idx_users_status_created ON users(status, created_at);

-- 工作流执行表索引
CREATE INDEX CONCURRENTLY idx_workflow_executions_user_id ON workflow_executions(user_id);
CREATE INDEX CONCURRENTLY idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX CONCURRENTLY idx_workflow_executions_created_at ON workflow_executions(created_at);
```

#### 2. 缓存策略

**Redis 缓存配置**:
```python
# shared_kernel/infrastructure/cache/redis_cache.py
import redis.asyncio as redis
import json
from typing import Any, Optional

class RedisCache:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        await self.redis.setex(
            key, 
            expire, 
            json.dumps(value, default=str)
        )
    
    async def delete(self, key: str):
        await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        return await self.redis.exists(key)

# 缓存装饰器
def cache_result(expire: int = 3600, key_prefix: str = ""):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached = await cache.get(cache_key)
            if cached is not None:
                return cached
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, expire)
            return result
        return wrapper
    return decorator
```

#### 3. API 性能优化

**异步处理**:
```python
# 使用异步处理提高并发性能
import asyncio
from concurrent.futures import ThreadPoolExecutor

# CPU密集型任务使用线程池
executor = ThreadPoolExecutor(max_workers=4)

@router.post("/process-data")
async def process_data(data: DataModel):
    # 异步处理多个任务
    tasks = [
        asyncio.create_task(process_item(item))
        for item in data.items
    ]
    
    results = await asyncio.gather(*tasks)
    return {"results": results}

# CPU密集型任务
async def cpu_intensive_task(data):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor, 
        heavy_computation, 
        data
    )
    return result
```

**响应压缩**:
```python
# 启用响应压缩
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 安全配置

#### 1. HTTPS 配置

**Nginx SSL 配置**:
```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name api.workflow-platform.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 2. 安全中间件

```python
# api_gateway/middleware/security_middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

# 添加到应用
app.add_middleware(SecurityHeadersMiddleware)
```

### 备份和恢复

#### 1. 数据库备份

**自动备份脚本**:
```bash
#!/bin/bash
# backup.sh

DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups"
DB_NAME="workflow_platform"
DB_USER="postgres"
DB_HOST="localhost"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 数据库备份
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# 保留最近30天的备份
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_backup_$DATE.sql.gz"
```

**定时任务**:
```bash
# 添加到 crontab
# 每天凌晨2点执行备份
0 2 * * * /path/to/backup.sh
```

#### 2. 应用数据备份

**文件备份**:
```bash
#!/bin/bash
# backup_files.sh

DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups"
APP_DIR="/app"

# 备份应用文件（排除日志和临时文件）
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
    --exclude='*.log' \
    --exclude='__pycache__' \
    --exclude='node_modules' \
    --exclude='.git' \
    $APP_DIR

echo "App backup completed: app_backup_$DATE.tar.gz"
```

### 故障排除

#### 1. 常见问题

**数据库连接问题**:
```bash
# 检查数据库连接
psql -h localhost -U postgres -d workflow_platform -c "SELECT 1;"

# 检查连接数
psql -h localhost -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# 查看慢查询
psql -h localhost -U postgres -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

**Redis 连接问题**:
```bash
# 检查 Redis 连接
redis-cli ping

# 查看 Redis 信息
redis-cli info

# 监控 Redis 命令
redis-cli monitor
```

**应用日志分析**:
```bash
# 查看应用日志
tail -f /var/log/workflow-platform/app.log

# 过滤错误日志
grep "ERROR" /var/log/workflow-platform/app.log

# 分析访问模式
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr
```

#### 2. 性能诊断

**系统资源监控**:
```bash
# CPU 使用率
top -p $(pgrep -f "uvicorn")

# 内存使用
ps aux | grep uvicorn

# 磁盘 I/O
iostat -x 1

# 网络连接
netstat -an | grep :8000
```

**应用性能分析**:
```python
# 添加性能监控装饰器
import time
import functools

def monitor_performance(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logger.info(f"Function {func.__name__} took {duration:.2f} seconds")
    return wrapper

# 使用示例
@monitor_performance
async def slow_operation():
    # 耗时操作
    pass
```

## 📚 相关文档

- [用户模块API文档](./user-module-api.md)
- [邮箱验证码API指南](./api/VERIFICATION_CODE_API_GUIDE.md)
- [开发规则](./workflow/DEVELOPMENT_RULES.md)
- [Git工作流](./workflow/GIT_WORKFLOW.md)
- [架构设计文档](../ARCHITECTURE.md)

## 🔄 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 完整的用户认证系统
- 基础工作流功能
- Docker容器化支持
- API文档完善

### v1.1.0 (计划中)
- 订阅计费系统
- 小红书数据采集
- 代理池管理
- 性能优化
- 监控告警系统

---

**注意**: 本文档会随着项目发展持续更新，请定期查看最新版本。如有问题或建议，请提交Issue或Pull Request。