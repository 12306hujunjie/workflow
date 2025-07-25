# Workflow Platform 开发规则

## 1. 架构规则

### 1.1 领域驱动设计 (DDD) 规则

- **限界上下文隔离**: 每个 `bounded_contexts` 下的模块必须保持独立，不能直接导入其他上下文的内部实现
- **共享内核使用**: 公共功能必须放在 `shared_kernel` 中，包括基础设施、领域基类等
- **依赖方向**: 依赖关系必须从外层指向内层（API → Application → Domain → Infrastructure）
- **事件驱动**: 跨上下文通信必须通过 `event_driven_coordination` 中的事件机制

### 1.2 目录结构规则

```
bounded_contexts/
├── {context_name}/
│   ├── domain/          # 领域层（实体、值对象、领域服务）
│   ├── application/     # 应用层（用例、应用服务）
│   ├── infrastructure/  # 基础设施层（仓储实现、外部服务）
│   └── presentation/    # 表现层（API路由、DTO）
```

### 1.3 API 网关规则

- 所有外部请求必须通过 `api_gateway` 进入
- 路由配置在 `api_gateway/routers/` 中按功能模块组织
- 中间件统一在 `api_gateway/middleware/` 中管理

## 2. 代码质量规则

### 2.1 Python 代码规范

- **格式化**: 使用 `black` 进行代码格式化
- **代码检查**: 使用 `flake8` 进行代码风格检查
- **类型检查**: 使用 `mypy` 进行静态类型检查
- **导入排序**: 使用 `isort` 进行导入语句排序

### 2.2 命名规范

- **文件名**: 使用小写字母和下划线 (`snake_case`)
- **类名**: 使用大驼峰命名 (`PascalCase`)
- **函数/变量名**: 使用小写字母和下划线 (`snake_case`)
- **常量**: 使用大写字母和下划线 (`UPPER_SNAKE_CASE`)

### 2.3 文档规范

- 所有公共函数和类必须有 docstring
- 使用 Google 风格的 docstring 格式
- API 端点必须有完整的 OpenAPI 文档

## 3. 测试规则

### 3.1 测试组织

- **单元测试**: 放在 `tests/unit/` 目录下
- **集成测试**: 放在 `tests/integration/` 目录下
- **测试文件命名**: `test_{module_name}.py`

### 3.2 测试覆盖率

- 单元测试覆盖率不低于 80%
- 核心业务逻辑覆盖率不低于 95%
- 使用 `pytest-cov` 生成覆盖率报告

### 3.3 测试数据

- 使用 `pytest` fixtures 管理测试数据
- 测试数据库使用独立的测试环境
- 每个测试用例必须独立，不依赖其他测试

## 4. 依赖管理规则

### 4.1 包管理

- 生产依赖写入 `requirements.txt`
- 开发依赖写入 `requirements-dev.txt`
- 使用固定版本号，避免版本冲突

### 4.2 依赖注入

- 使用 `dependency-injector` 进行依赖注入
- 容器配置在 `container.py` 中统一管理
- 避免循环依赖

## 5. 数据库规则

### 5.1 迁移管理

- 使用 `alembic` 管理数据库迁移
- 迁移文件必须有描述性的名称
- 每个迁移必须可回滚

### 5.2 模型定义

- 数据库模型放在各自上下文的 `infrastructure/models/` 中
- 使用 SQLAlchemy 2.0 语法
- 模型必须有适当的索引和约束

## 6. API 设计规则

### 6.1 RESTful 设计

- 遵循 REST 原则设计 API
- 使用标准 HTTP 状态码
- 统一的错误响应格式

### 6.2 版本控制

- API 版本通过 URL 路径控制 (`/api/v1/`)
- 向后兼容性保持至少两个版本

### 6.3 请求/响应格式

- 使用 Pydantic 模型定义请求和响应
- 统一的分页格式
- 统一的错误响应格式

## 7. 安全规则

### 7.1 认证授权

- 使用 JWT 进行身份认证
- 敏感操作需要权限验证
- 密码使用 bcrypt 加密

### 7.2 配置管理

- 敏感配置使用环境变量
- 不在代码中硬编码密钥
- 使用 `.env` 文件管理本地配置

### 7.3 输入验证

- 所有用户输入必须验证
- 使用 Pydantic 进行数据验证
- 防止 SQL 注入和 XSS 攻击

## 8. 开发流程规则

### 8.1 Git 工作流

- 使用 Git Flow 分支模型
- 功能开发在 `feature/` 分支
- 提交信息使用约定式提交格式

### 8.2 代码审查

- 所有代码必须经过 Code Review
- PR 必须通过所有自动化检查
- 至少一个团队成员的批准

### 8.3 CI/CD 规则

- 每次提交触发自动化测试
- 测试通过后自动部署到测试环境
- 生产部署需要手动批准

## 9. 性能规则

### 9.1 数据库性能

- 避免 N+1 查询问题
- 使用适当的数据库索引
- 大数据量查询使用分页

### 9.2 缓存策略

- 使用 Redis 缓存频繁访问的数据
- 设置合适的缓存过期时间
- 缓存键命名规范

### 9.3 异步处理

- 长时间运行的任务使用 Prefect 异步处理
- 避免阻塞主线程
- 合理使用连接池

## 10. 监控和日志规则

### 10.1 日志规范

- 使用结构化日志格式
- 不同级别的日志分类记录
- 敏感信息不记录到日志

### 10.2 错误处理

- 统一的异常处理机制
- 详细的错误信息记录
- 用户友好的错误提示

## 11. 工具和脚本

### 11.1 开发工具

- 使用 `make` 命令简化常用操作
- 开发脚本放在 `scripts/` 目录
- Docker 容器化开发环境

### 11.2 代码质量检查

```bash
# 运行所有代码质量检查
make lint

# 运行测试
make test

# 格式化代码
make format
```

## 12. 文档规则

### 12.1 项目文档

- README.md 包含项目概述和快速开始
- ARCHITECTURE.md 描述系统架构
- API 文档自动生成

### 12.2 代码文档

- 复杂业务逻辑必须有注释
- 公共接口必须有文档
- 配置文件必须有说明

---

## 执行检查清单

在提交代码前，请确保：

- [ ] 代码通过所有测试
- [ ] 代码格式化正确
- [ ] 类型检查通过
- [ ] 代码覆盖率达标
- [ ] 文档更新完整
- [ ] 安全检查通过
- [ ] 性能测试通过

## 违规处理

- 轻微违规：代码审查时指出并要求修改
- 严重违规：拒绝合并，要求重新开发
- 重复违规：团队讨论改进措施

---

*本规则文档会根据项目发展持续更新，所有团队成员都有责任遵守和完善这些规则。*