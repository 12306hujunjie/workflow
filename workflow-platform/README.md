# Workflow Platform - 服务导向自动化工作流平台

基于DDD架构和事件驱动设计的SaaS自动化工作流平台，支持多平台数据采集、用户订阅计费、智能代理池管理等功能。

## 技术栈

- **后端框架**: FastAPI + SQLAlchemy 2.0 (异步)
- **数据验证**: Pydantic v2
- **依赖注入**: Dependency Injector
- **工作流编排**: Prefect 3.0
- **数据库**: PostgreSQL 15+ / Redis 7+
- **认证**: JWT + BCrypt
- **容器化**: Docker + Docker Compose

## 项目结构

```
workflow-platform/
├── shared_kernel/           # 共享内核
├── bounded_contexts/        # 限界上下文
│   ├── user_management/    # 用户管理
│   ├── subscription/       # 订阅计费
│   ├── xiaohongshu/       # 小红书服务
│   ├── qidian/            # 起点服务
│   └── proxy_pool/        # 代理池
├── api_gateway/           # API网关
├── config/                # 配置
└── migrations/            # 数据库迁移
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/yourusername/workflow-platform.git
cd workflow-platform

# 复制环境变量配置
cp .env.example .env

# 编辑.env文件，修改必要的配置
# 特别是JWT_SECRET_KEY需要修改为安全的密钥
```

### 2. 使用Docker Compose运行

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down
```

### 3. 本地开发运行

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动PostgreSQL和Redis（使用Docker）
docker-compose up -d postgres redis

# 运行数据库迁移
psql -h localhost -U postgres -d workflow_platform -f migrations/user_management.sql

# 启动应用
uvicorn api_gateway.main:app --reload
```

## API文档

启动应用后，可以访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 用户管理API示例

### 注册用户
```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test@123456"
  }'
```

### 用户登录
```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_email": "testuser",
    "password": "Test@123456"
  }'
```

### 获取当前用户信息
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 功能模块

### 已完成
- ✅ 用户注册和登录
- ✅ JWT认证和授权
- ✅ 用户资料管理
- ✅ 密码修改
- ✅ DDD分层架构
- ✅ 依赖注入容器
- ✅ Docker容器化

### 待开发
- ⏳ 订阅计费系统
- ⏳ 小红书服务集成
- ⏳ 起点数据采集
- ⏳ 代理池管理
- ⏳ Prefect工作流集成
- ⏳ 前端界面

## 测试

```bash
# 运行单元测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html

# 代码格式化
black .

# 代码检查
flake8 .
mypy .
```

## 部署

### 生产环境配置建议

1. 修改`.env`文件中的所有敏感配置
2. 使用强密码和安全的JWT密钥
3. 配置HTTPS
4. 设置适当的CORS策略
5. 配置日志收集和监控

### 使用Docker部署

```bash
# 构建生产镜像
docker build -t workflow-platform:latest .

# 运行容器
docker run -d \
  --name workflow-platform \
  -p 8000:8000 \
  --env-file .env \
  workflow-platform:latest
```

## 贡献指南

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情