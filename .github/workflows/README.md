# GitHub Actions 工作流说明

## 工作流文件

### 1. unit-tests.yml - 单元测试工作流
这是主要的单元测试工作流，会在以下情况触发：
- 推送到 master 或 main 分支
- 创建 Pull Request
- 仅当 workflow-platform 目录下的文件有变化时

**功能：**
- 运行所有单元测试
- 生成测试覆盖率报告
- 上传覆盖率到 Codecov（需要配置 CODECOV_TOKEN）

### 2. test.yml - 完整测试和代码质量检查
更全面的工作流，包括：
- 单元测试和集成测试
- 代码风格检查（flake8, black, isort）
- 类型检查（mypy）
- 使用真实的 PostgreSQL 和 Redis 服务

## 设置说明

### 1. 启用 GitHub Actions
工作流会自动在推送代码后运行，无需额外配置。

### 2. 配置 Codecov（可选）
如果想要代码覆盖率报告：
1. 访问 https://codecov.io/
2. 使用 GitHub 账号登录
3. 添加你的仓库
4. 获取 CODECOV_TOKEN
5. 在 GitHub 仓库设置中添加 Secret：
   - Name: `CODECOV_TOKEN`
   - Value: 从 Codecov 获取的 token

### 3. 查看测试结果
- 在 GitHub 仓库的 Actions 标签页查看运行结果
- 在 Pull Request 中查看测试状态
- 如果配置了 Codecov，可以看到覆盖率报告

## 本地运行测试

模拟 GitHub Actions 环境运行测试：

```bash
# 进入项目目录
cd workflow-platform

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 运行单元测试
pytest tests/unit -v

# 运行测试并生成覆盖率
pytest tests/unit --cov=bounded_contexts --cov=shared_kernel --cov-report=html
```

## 徽章

在 README.md 中添加状态徽章：

```markdown
![Unit Tests](https://github.com/12306hujunjie/workflow/actions/workflows/unit-tests.yml/badge.svg)
![Tests](https://github.com/12306hujunjie/workflow/actions/workflows/test.yml/badge.svg)
```

## 故障排除

### 测试失败
1. 检查 Actions 日志了解详细错误信息
2. 确保所有依赖都在 requirements.txt 中
3. 确保测试可以在本地运行

### 依赖问题
1. 清除缓存：在 Actions 页面手动触发工作流时选择清除缓存
2. 更新依赖版本

### 权限问题
确保 GitHub Actions 有正确的权限：
- Settings → Actions → General → Workflow permissions
- 选择 "Read and write permissions"