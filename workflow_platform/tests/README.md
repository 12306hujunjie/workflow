# 测试说明

## 测试结构

```
tests/
├── conftest.py          # Pytest配置和通用fixtures
├── unit/                # 单元测试
│   ├── test_user_entity.py           # 用户实体测试
│   ├── test_user_repository.py       # 用户仓储测试
│   ├── test_user_application_service.py  # 用户应用服务测试
│   └── test_auth_services.py         # 认证服务测试
└── integration/         # 集成测试
    └── test_user_api.py              # 用户API测试
```

## 运行测试

### 运行所有测试
```bash
pytest -v
```

### 运行单元测试
```bash
pytest tests/unit -v
```

### 运行集成测试
```bash
pytest tests/integration -v
```

### 生成测试覆盖率报告
```bash
pytest --cov=. --cov-report=html --cov-report=term
```

### 使用Makefile运行测试
```bash
make test           # 运行所有测试
make test-unit      # 运行单元测试
make test-integration  # 运行集成测试
make coverage       # 生成覆盖率报告
```

## 测试覆盖范围

### 单元测试

1. **用户实体测试** (`test_user_entity.py`)
   - 用户创建和初始化
   - 用户激活流程
   - 用户暂停和重新激活
   - 登录记录
   - 密码更新
   - 资料更新
   - 领域事件管理
   - 值对象验证（用户名、邮箱、密码）

2. **用户仓储测试** (`test_user_repository.py`)
   - 保存新用户
   - 更新已存在用户
   - 通过ID/用户名/邮箱查找
   - 删除用户
   - 分页查询
   - 统计用户数量
   - 检查用户名/邮箱是否存在

3. **应用服务测试** (`test_user_application_service.py`)
   - 用户注册流程
   - 用户登录流程
   - 获取用户资料
   - 更新用户资料
   - 修改密码
   - 激活用户账户

4. **认证服务测试** (`test_auth_services.py`)
   - 密码哈希和验证
   - JWT令牌创建
   - JWT令牌验证
   - 刷新令牌机制

### 集成测试

1. **用户API测试** (`test_user_api.py`)
   - 完整的注册登录流程
   - 并发注册处理
   - 输入验证（密码、用户名、邮箱）
   - API错误处理

## 测试最佳实践

1. **使用Fixtures**
   - 使用`conftest.py`中定义的fixtures来减少代码重复
   - 为测试数据创建专门的fixtures

2. **测试隔离**
   - 每个测试应该独立运行
   - 使用事务回滚确保测试之间不相互影响

3. **Mock外部依赖**
   - 使用`unittest.mock`或`pytest-mock`来模拟外部服务
   - 专注于测试业务逻辑

4. **测试命名**
   - 使用描述性的测试名称
   - 遵循`test_<被测试的功能>_<场景>_<期望结果>`格式

5. **测试覆盖率**
   - 目标覆盖率：80%以上
   - 重点覆盖业务逻辑和边界情况

## 持续集成

建议在CI/CD管道中集成以下步骤：

1. 运行所有测试
2. 检查测试覆盖率
3. 生成测试报告
4. 代码质量检查（lint、type check）

## 故障排除

### 常见问题

1. **导入错误**
   - 确保在项目根目录运行测试
   - 检查`PYTHONPATH`设置

2. **数据库连接错误**
   - 测试使用PostgreSQL测试数据库
- 确保已安装`asyncpg`并配置PostgreSQL

3. **异步测试问题**
   - 使用`@pytest.mark.asyncio`装饰器
   - 确保`pytest-asyncio`已安装