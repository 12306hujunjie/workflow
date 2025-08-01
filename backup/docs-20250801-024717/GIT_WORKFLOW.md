# Git 工作流规范

## 分支策略

### 主要分支

- **main**: 生产环境分支，始终保持可部署状态
- **develop**: 开发主分支，集成最新的开发功能
- **release/x.x.x**: 发布准备分支
- **hotfix/xxx**: 紧急修复分支

### 功能分支

- **feature/xxx**: 新功能开发分支
- **bugfix/xxx**: Bug修复分支
- **refactor/xxx**: 代码重构分支
- **docs/xxx**: 文档更新分支

## 分支命名规范

```
类型/简短描述

示例:
feature/user-authentication
bugfix/login-validation-error
refactor/database-connection-pool
docs/api-documentation-update
hotfix/security-vulnerability-fix
```

## 提交信息规范

### 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- **feat**: 新功能
- **fix**: Bug修复
- **docs**: 文档更新
- **style**: 代码格式调整（不影响功能）
- **refactor**: 代码重构
- **perf**: 性能优化
- **test**: 测试相关
- **chore**: 构建过程或辅助工具的变动
- **ci**: CI/CD相关变更
- **build**: 构建系统或外部依赖变更
- **revert**: 回滚之前的提交

### Scope 范围（可选）

- **auth**: 认证相关
- **user**: 用户管理
- **workflow**: 工作流
- **api**: API相关
- **db**: 数据库相关
- **config**: 配置相关
- **test**: 测试相关

### 提交信息示例

```bash
# 新功能
feat(auth): add JWT token refresh mechanism

# Bug修复
fix(user): resolve email validation error in registration

# 文档更新
docs(api): update authentication endpoint documentation

# 重构
refactor(db): optimize database connection pooling

# 性能优化
perf(workflow): improve task execution performance

# 测试
test(auth): add unit tests for login functionality
```

## 工作流程

### 1. 功能开发流程

```bash
# 1. 从develop分支创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 开发功能
# ... 编写代码 ...

# 3. 提交代码
git add .
git commit -m "feat(scope): add new feature description"

# 4. 推送到远程
git push origin feature/new-feature

# 5. 创建Pull Request到develop分支
# 6. 代码审查通过后合并
# 7. 删除功能分支
git branch -d feature/new-feature
git push origin --delete feature/new-feature
```

### 2. Bug修复流程

```bash
# 1. 从develop分支创建修复分支
git checkout develop
git pull origin develop
git checkout -b bugfix/fix-issue

# 2. 修复Bug
# ... 修复代码 ...

# 3. 提交修复
git add .
git commit -m "fix(scope): resolve specific issue description"

# 4. 推送并创建PR
git push origin bugfix/fix-issue
```

### 3. 紧急修复流程

```bash
# 1. 从main分支创建hotfix分支
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# 2. 修复问题
# ... 修复代码 ...

# 3. 提交修复
git add .
git commit -m "fix: resolve critical security issue"

# 4. 合并到main和develop
git checkout main
git merge hotfix/critical-fix
git push origin main

git checkout develop
git merge hotfix/critical-fix
git push origin develop

# 5. 创建版本标签
git tag -a v1.0.1 -m "Hotfix release v1.0.1"
git push origin v1.0.1

# 6. 删除hotfix分支
git branch -d hotfix/critical-fix
```

### 4. 发布流程

```bash
# 1. 从develop创建release分支
git checkout develop
git pull origin develop
git checkout -b release/1.1.0

# 2. 准备发布（更新版本号、文档等）
# ... 更新版本信息 ...

# 3. 提交发布准备
git add .
git commit -m "chore(release): prepare for version 1.1.0"

# 4. 合并到main
git checkout main
git merge release/1.1.0
git push origin main

# 5. 创建版本标签
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0

# 6. 合并回develop
git checkout develop
git merge release/1.1.0
git push origin develop

# 7. 删除release分支
git branch -d release/1.1.0
```

## Pull Request 规范

### PR标题格式

```
<type>(<scope>): <description>

示例:
feat(auth): implement OAuth2 authentication
fix(user): resolve registration validation issue
```

### PR描述模板

参考 `.github/PULL_REQUEST_TEMPLATE.md`

### PR审查要求

- 至少一个团队成员审查
- 所有自动化检查通过
- 代码覆盖率达标
- 文档更新完整

## 代码审查清单

### 功能性检查

- [ ] 功能实现正确
- [ ] 边界条件处理
- [ ] 错误处理完善
- [ ] 性能考虑

### 代码质量检查

- [ ] 代码可读性
- [ ] 命名规范
- [ ] 注释充分
- [ ] 复杂度合理

### 架构检查

- [ ] 遵循DDD原则
- [ ] 依赖方向正确
- [ ] 接口设计合理
- [ ] 模块职责清晰

### 测试检查

- [ ] 单元测试充分
- [ ] 集成测试覆盖
- [ ] 测试用例质量
- [ ] 测试数据合理

## Git Hooks

### Pre-commit Hook

```bash
# 安装pre-commit
pip install pre-commit
pre-commit install

# 运行所有检查
pre-commit run --all-files
```

### Commit-msg Hook

验证提交信息格式是否符合规范

## 版本管理

### 语义化版本

遵循 [Semantic Versioning](https://semver.org/) 规范：

- **MAJOR**: 不兼容的API变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修正

### 版本标签

```bash
# 创建版本标签
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 查看所有标签
git tag -l

# 删除标签
git tag -d v1.0.0
git push origin --delete v1.0.0
```

## 常用Git命令

### 日常操作

```bash
# 查看状态
git status

# 查看差异
git diff
git diff --staged

# 查看提交历史
git log --oneline --graph

# 查看分支
git branch -a

# 切换分支
git checkout branch-name
git switch branch-name  # Git 2.23+

# 创建并切换分支
git checkout -b new-branch
git switch -c new-branch  # Git 2.23+
```

### 同步操作

```bash
# 拉取最新代码
git pull origin main

# 推送代码
git push origin branch-name

# 强制推送（谨慎使用）
git push --force-with-lease origin branch-name
```

### 撤销操作

```bash
# 撤销工作区修改
git checkout -- file-name
git restore file-name  # Git 2.23+

# 撤销暂存区修改
git reset HEAD file-name
git restore --staged file-name  # Git 2.23+

# 撤销最后一次提交
git reset --soft HEAD~1

# 修改最后一次提交信息
git commit --amend
```

### 合并操作

```bash
# 合并分支
git merge feature-branch

# 变基合并
git rebase main

# 交互式变基
git rebase -i HEAD~3
```

## 冲突解决

### 合并冲突

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 解决冲突文件
# 编辑冲突文件，删除冲突标记

# 3. 标记冲突已解决
git add conflicted-file

# 4. 完成合并
git commit
```

### 变基冲突

```bash
# 1. 开始变基
git rebase main

# 2. 解决冲突
# 编辑冲突文件

# 3. 继续变基
git add conflicted-file
git rebase --continue

# 4. 如需中止变基
git rebase --abort
```

## 最佳实践

### 提交频率

- 小而频繁的提交
- 每个提交只做一件事
- 提交前确保代码可运行

### 分支管理

- 及时删除已合并的分支
- 定期同步主分支代码
- 避免长期存在的功能分支

### 代码同步

- 每日开始工作前拉取最新代码
- 推送前先拉取并解决冲突
- 使用 `git pull --rebase` 保持提交历史整洁

### 安全考虑

- 不提交敏感信息（密码、密钥等）
- 使用 `.gitignore` 排除不必要的文件
- 定期审查提交历史

---

**注意**: 本工作流规范是团队协作的基础，所有团队成员都应严格遵守。如有疑问或建议，请及时与团队讨论。