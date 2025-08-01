# Workflow Platform

![Unit Tests](https://github.com/12306hujunjie/workflow/actions/workflows/unit-tests.yml/badge.svg)
![Tests](https://github.com/12306hujunjie/workflow/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/12306hujunjie/workflow/branch/master/graph/badge.svg)](https://codecov.io/gh/12306hujunjie/workflow)

服务导向的自动化工作流SaaS平台，基于领域驱动设计(DDD)和事件驱动架构。

## 核心功能

- 🔐 **用户管理系统** - JWT认证、角色权限管理
- 💰 **订阅计费系统** - 基于服务的阶梯式计费模型
- 📱 **小红书服务** - API管理、账号管理、数据采集
- 📚 **起点服务** - 热榜数据抓取、小说信息采集
- 🌐 **代理池管理** - 智能代理轮换、健康检查
- 🔄 **工作流编排** - 基于Prefect的自动化工作流

## 技术架构

- **后端**: FastAPI + SQLAlchemy 2.0 (异步)
- **架构**: Domain-Driven Design (DDD) + Event-Driven
- **数据验证**: Pydantic v2
- **依赖注入**: Dependency Injector
- **工作流**: Prefect 3.0
- **数据库**: PostgreSQL 15+ / Redis 7+
- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## 快速开始

```bash
# 克隆项目
git clone https://github.com/12306hujunjie/workflow.git
cd workflow/workflow-platform

# 安装依赖
pip install -r requirements.txt

# 启动服务
docker-compose up -d

# 运行应用
uvicorn api_gateway.main:app --reload
```

## 📚 文档导航

- **[API和部署指南](docs/API_AND_DEPLOYMENT_GUIDE.md)** - 🔥 **推荐** 完整的API文档、架构设计和部署指南
- [项目架构文档](ARCHITECTURE.md) - 系统架构和设计原则
- [用户模块API](docs/user-module-api.md) - 用户认证和管理API
- [开发规则](docs/workflow/DEVELOPMENT_RULES.md) - 开发规范和最佳实践
- [Git工作流](docs/workflow/GIT_WORKFLOW.md) - 代码提交和分支管理
- [后端详细说明](workflow-platform/README.md) - 后端项目具体信息

## 项目结构

```
workflow/
├── .github/workflows/      # GitHub Actions配置
├── workflow-platform/      # 主应用代码
│   ├── bounded_contexts/   # 限界上下文（DDD）
│   ├── shared_kernel/      # 共享内核
│   ├── api_gateway/        # API网关
│   ├── tests/              # 测试代码
│   └── docker-compose.yml  # Docker配置
└── ARCHITECTURE.md         # 架构设计文档
```

## 开发状态

### 已完成 ✅
- 用户管理模块（注册、登录、认证）
- JWT Token认证系统
- DDD分层架构实现
- 依赖注入容器配置
- 单元测试和集成测试
- GitHub Actions CI/CD
- Docker容器化部署

### 开发中 🚧
- 订阅计费系统
- 小红书服务集成
- Prefect工作流集成

### 计划中 📋
- 起点数据采集服务
- 代理池管理系统
- 前端用户界面
- 监控和日志系统

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 测试

```bash
# 运行单元测试
cd workflow-platform
pytest tests/unit -v

# 运行所有测试并生成覆盖率
pytest --cov=. --cov-report=html
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件