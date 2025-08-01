# GitHub Actions 设置指南

## 已配置的工作流

### 1. 单元测试工作流 (unit-tests.yml)
- **触发条件**: 推送到master/main分支，或PR到这些分支
- **运行内容**: 
  - Python 3.10环境
  - 安装依赖
  - 运行单元测试
  - 生成测试覆盖率
  - 上传到Codecov（可选）

### 2. 完整测试工作流 (test.yml)
- **触发条件**: 同上
- **运行内容**:
  - 单元测试和集成测试
  - 代码质量检查(flake8, black, isort, mypy)
  - 使用真实PostgreSQL和Redis服务
  - 更全面的测试覆盖

## 使用说明

### 基本使用
1. 推送代码到GitHub后，Actions会自动运行
2. 在Pull Request中可以看到测试状态
3. 点击Details查看详细日志

### 查看测试结果
- 访问仓库的Actions标签页
- 选择具体的工作流运行记录
- 查看每个步骤的执行结果

### 添加Codecov（可选）
1. 访问 https://codecov.io/
2. 用GitHub账号登录
3. 选择你的仓库
4. 获取CODECOV_TOKEN
5. 在GitHub仓库Settings → Secrets → Actions中添加
   - Name: CODECOV_TOKEN
   - Value: 你的token

## 本地测试

在提交前本地运行测试：

```bash
cd workflow_platform

# 安装测试依赖
pip install -r requirements-dev.txt

# 运行单元测试
pytest tests/unit -v

# 检查代码风格
black --check .
flake8 .

# 运行所有检查
make test
make lint
```

## 常见问题

### Q: 测试失败了怎么办？
A: 查看Actions日志，找到具体失败的测试，在本地复现并修复

### Q: 如何跳过CI？
A: 在commit message中添加 [skip ci] 或 [ci skip]

### Q: 如何重新运行失败的工作流？
A: 在Actions页面找到失败的运行，点击"Re-run all jobs"

## 优化建议

1. **缓存优化**: 已配置pip缓存，加快依赖安装
2. **并行运行**: test和lint作为独立job并行运行
3. **条件运行**: 仅在相关文件变更时运行

## 扩展

可以根据需要添加更多工作流：
- 自动部署
- 安全扫描
- 性能测试
- 文档生成