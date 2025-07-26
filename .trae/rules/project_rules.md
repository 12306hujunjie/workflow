# Workflow Platform 项目专属规则

## 1. 项目概述

### 1.1 技术栈

**前端技术栈：**
- React 19.1.0 + TypeScript
- Vite 7.0.4 (构建工具)
- Ant Design 5.26.6 (UI组件库)
- Tailwind CSS 4.1.11 (样式框架)
- Zustand 5.0.6 (状态管理)
- React Router DOM 7.7.1 (路由)
- Axios 1.11.0 (HTTP客户端)
- Day.js 1.11.13 (日期处理)

**后端技术栈：**
- Python 3.10+ + FastAPI
- SQLAlchemy 2.0 (ORM)
- Alembic (数据库迁移)
- PostgreSQL (主数据库)
- Redis (缓存)
- JWT (身份认证)
- Prefect (工作流引擎)
- Docker (容器化)

### 1.2 项目结构

```
workflow/
├── frontend/                 # React前端应用
├── workflow-platform/        # Python后端应用
├── docs/                    # 项目文档
├── .github/workflows/       # GitHub Actions CI/CD
└── .trae/rules/            # 项目规则文档
```

## 2. 架构设计规则

### 2.1 领域驱动设计 (DDD)

- **限界上下文隔离**: 每个 `bounded_contexts` 下的模块必须保持独立
- **共享内核**: 公共功能放在 `shared_kernel` 中
- **依赖方向**: API → Application → Domain → Infrastructure
- **事件驱动**: 跨上下文通信通过 `event_driven_coordination`

### 2.2 后端目录结构

```
bounded_contexts/
├── {context_name}/
│   ├── domain/          # 领域层（实体、值对象、领域服务）
│   ├── application/     # 应用层（用例、应用服务）
│   ├── infrastructure/  # 基础设施层（仓储实现、外部服务）
│   └── presentation/    # 表现层（API路由、DTO）
```

### 2.3 前端目录结构

```
src/
├── components/          # 可复用组件
├── pages/              # 页面组件
├── hooks/              # 自定义Hooks
├── services/           # API服务
├── store/              # 状态管理
├── types/              # TypeScript类型定义
├── utils/              # 工具函数
└── router/             # 路由配置
```

## 3. 前端开发规则

### 3.1 React组件规范

- 使用函数组件 + Hooks
- 组件名使用 PascalCase
- 文件名使用 PascalCase (如: `UserProfile.tsx`)
- 一个文件一个组件（除非是紧密相关的小组件）

### 3.2 TypeScript规范

- 严格模式开启
- 所有组件Props必须定义接口
- 避免使用 `any` 类型
- API响应数据必须定义类型

### 3.3 样式规范

- 优先使用 Tailwind CSS 类
- 复杂样式使用 CSS Modules 或 styled-components
- 响应式设计遵循移动优先原则
- 使用 Ant Design 主题定制

### 3.4 状态管理规范

- 使用 Zustand 进行全局状态管理
- 本地状态优先使用 useState
- 复杂状态逻辑使用 useReducer
- 异步状态使用自定义 Hooks 封装

## 4. 后端开发规则

### 4.1 API设计规范

- 遵循 RESTful 设计原则
- 使用标准 HTTP 状态码
- API版本控制: `/api/v1/`
- 统一的错误响应格式
- 使用 Pydantic 模型进行数据验证

### 4.2 数据库规范

- 使用 SQLAlchemy 2.0 语法
- 模型定义在各自上下文的 `infrastructure/models/`
- 使用 Alembic 管理数据库迁移
- 迁移文件必须有描述性名称
- 每个迁移必须可回滚

### 4.3 依赖注入规范

- 使用 `dependency-injector` 进行依赖注入
- 容器配置在 `container.py` 中统一管理
- 避免循环依赖
- 接口与实现分离

## 5. 代码质量和规范

### 5.1 Python代码规范

- **格式化**: 使用 `black` (行长度88)
- **代码检查**: 使用 `flake8`
- **类型检查**: 使用 `mypy`
- **导入排序**: 使用 `isort`
- **安全检查**: 使用 `bandit`

### 5.2 前端代码规范

- **ESLint**: 使用 TypeScript ESLint 配置
- **格式化**: 使用 Prettier (通过ESLint集成)
- **类型检查**: TypeScript 严格模式
- **组件检查**: React Hooks 规则

### 5.3 命名规范

**Python:**
- 文件名: `snake_case`
- 类名: `PascalCase`
- 函数/变量: `snake_case`
- 常量: `UPPER_SNAKE_CASE`

**TypeScript/React:**
- 组件名: `PascalCase`
- 文件名: `PascalCase.tsx`
- 函数/变量: `camelCase`
- 常量: `UPPER_SNAKE_CASE`
- 接口: `IPascalCase` 或 `PascalCase`

### 5.4 文档规范

- Python: 使用 Google 风格的 docstring
- TypeScript: 使用 JSDoc 注释
- API: 完整的 OpenAPI 文档
- README: 每个模块都要有说明文档

## 6. 测试策略

### 6.1 后端测试

- **单元测试**: `tests/unit/` (覆盖率 ≥ 80%)
- **集成测试**: `tests/integration/`
- **测试框架**: pytest + pytest-cov
- **测试数据**: 使用 fixtures 管理
- **测试数据库**: 独立的测试环境

### 6.2 前端测试

- **单元测试**: Jest + React Testing Library
- **组件测试**: 测试组件行为和交互
- **E2E测试**: Playwright (可选)
- **类型检查**: TypeScript 编译检查

### 6.3 测试规范

- 测试文件命名: `test_{module_name}.py` 或 `{Component}.test.tsx`
- 每个测试用例必须独立
- 测试描述要清晰明确
- 核心业务逻辑覆盖率 ≥ 95%

## 7. Git工作流规则

### 7.1 分支策略

- **main**: 生产环境分支
- **develop**: 开发主分支
- **feature/xxx**: 新功能开发
- **bugfix/xxx**: Bug修复
- **hotfix/xxx**: 紧急修复
- **release/x.x.x**: 发布准备

### 7.2 提交信息规范

```
<type>(<scope>): <subject>

类型:
- feat: 新功能
- fix: Bug修复
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

范围:
- auth: 认证
- user: 用户管理
- workflow: 工作流
- api: API
- ui: 用户界面
```

### 7.3 代码审查规则

- 所有代码必须经过 Code Review
- PR 必须通过所有自动化检查
- 至少一个团队成员批准
- 功能分支合并后删除

## 8. CI/CD流程

### 8.1 自动化检查

- **代码质量**: ESLint, flake8, black, isort
- **类型检查**: TypeScript, mypy
- **安全检查**: bandit
- **测试**: 单元测试 + 集成测试
- **覆盖率**: 代码覆盖率报告

### 8.2 部署流程

- **开发环境**: 推送到 develop 分支自动部署
- **测试环境**: PR 创建时自动部署预览
- **生产环境**: 合并到 main 分支手动部署
- **回滚**: 支持快速回滚到上一版本

### 8.3 环境配置

- 使用环境变量管理配置
- 不同环境使用不同的 `.env` 文件
- 敏感信息使用 GitHub Secrets

## 9. 部署规则

### 9.1 容器化

- 前端和后端都使用 Docker 容器化
- 使用 multi-stage build 优化镜像大小
- 生产镜像不包含开发依赖

### 9.2 服务配置

- **前端**: Nginx 静态文件服务
- **后端**: Uvicorn + Gunicorn
- **数据库**: PostgreSQL 主从配置
- **缓存**: Redis 集群
- **负载均衡**: Nginx 反向代理

### 9.3 监控和日志

- 结构化日志格式
- 不同级别的日志分类
- 敏感信息不记录到日志
- 性能监控和错误追踪

## 10. 安全规范

### 10.1 认证授权

- 使用 JWT 进行身份认证
- Token 过期时间设置合理
- 敏感操作需要权限验证
- 密码使用 bcrypt 加密

### 10.2 数据安全

- 所有用户输入必须验证
- 使用 Pydantic 进行数据验证
- 防止 SQL 注入和 XSS 攻击
- API 限流和防护

### 10.3 配置安全

- 敏感配置使用环境变量
- 不在代码中硬编码密钥
- 定期更新依赖包
- 使用 HTTPS 传输

## 11. 性能优化规则

### 11.1 前端性能

- 组件懒加载
- 图片优化和懒加载
- 代码分割和按需加载
- 使用 React.memo 优化渲染
- 合理使用 useMemo 和 useCallback

### 11.2 后端性能

- 数据库查询优化
- 使用适当的索引
- 避免 N+1 查询问题
- 使用 Redis 缓存
- 异步处理长时间任务

### 11.3 缓存策略

- API 响应缓存
- 静态资源缓存
- 数据库查询缓存
- 设置合适的缓存过期时间

## 12. 开发工具和脚本

### 12.1 开发环境

- **虚拟环境**: 项目统一使用 `/Users/hushengnian/PycharmProjects/workflow/.venv/bin/python` 作为Python解释器
- **启动服务器**: 必须使用虚拟环境的Python启动uvicorn，使用 `python3 -m uvicorn` 而不是直接使用 `uvicorn` 命令
- 使用 `make` 命令简化操作
- Docker Compose 本地开发环境
- 热重载开发服务器
- 统一的开发工具配置

### 12.2 常用命令

**后端:**
```bash
make run          # 启动开发服务器
make test         # 运行测试
make lint         # 代码检查
make format       # 代码格式化

# 手动启动开发服务器（使用虚拟环境）
source venv/bin/activate && python3 -m uvicorn api_gateway.main:app --host 0.0.0.0 --port 8001 --reload
```

**前端:**
```bash
npm run dev       # 启动开发服务器
npm run build     # 构建生产版本
npm run lint      # ESLint检查
npm run preview   # 预览构建结果
```

### 12.3 IDE配置

- VSCode 推荐插件配置
- 统一的代码格式化设置
- 调试配置
- 任务和快捷键配置

---

**注意**: 本文档会随着项目发展持续更新，所有团队成员都应该遵循这些规则，确保代码质量和项目的可维护性。