# PostgreSQL 数据库设置指南

## 1. 安装 PostgreSQL

### macOS (使用 Homebrew)
```bash
brew install postgresql
brew services start postgresql
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Windows
从 [PostgreSQL 官网](https://www.postgresql.org/download/windows/) 下载并安装。

## 2. 创建数据库和用户

```bash
# 连接到 PostgreSQL
sudo -u postgres psql

# 或者在 macOS 上
psql postgres
```

在 PostgreSQL 命令行中执行：

```sql
-- 创建用户
CREATE USER workflow_user WITH PASSWORD 'workflow_password';

-- 创建主数据库
CREATE DATABASE workflow_platform OWNER workflow_user;

-- 创建测试数据库
CREATE DATABASE workflow_platform_test OWNER workflow_user;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE workflow_platform TO workflow_user;
GRANT ALL PRIVILEGES ON DATABASE workflow_platform_test TO workflow_user;

-- 退出
\q
```

## 3. 验证连接

```bash
# 测试连接
psql -h localhost -U workflow_user -d workflow_platform
```

## 4. 环境配置

项目的 `.env` 文件已经配置为：
```
DATABASE_URL=postgresql+asyncpg://workflow_user:workflow_password@localhost:5432/workflow_platform
```

## 5. 运行数据库迁移

```bash
# 进入项目目录
cd workflow-platform

# 如果有 Alembic 迁移文件，运行迁移
alembic upgrade head

# 或者运行 SQL 迁移文件
psql -h localhost -U workflow_user -d workflow_platform -f migrations/user_management.sql
```

## 6. 安全建议

### 生产环境配置
- 使用强密码
- 限制数据库访问权限
- 使用 SSL 连接
- 定期备份数据库

### 示例生产环境配置
```
DATABASE_URL=postgresql+asyncpg://your_user:your_strong_password@your_host:5432/your_database?sslmode=require
```

## 7. 常用管理命令

```bash
# 查看数据库列表
psql -U workflow_user -l

# 连接到特定数据库
psql -U workflow_user -d workflow_platform

# 查看表结构
\dt

# 查看表详情
\d table_name

# 备份数据库
pg_dump -U workflow_user -h localhost workflow_platform > backup.sql

# 恢复数据库
psql -U workflow_user -h localhost workflow_platform < backup.sql
```

## 8. 故障排除

### 连接问题
- 确认 PostgreSQL 服务正在运行
- 检查防火墙设置
- 验证用户名和密码
- 确认数据库存在

### 权限问题
```sql
-- 重新授予权限
GRANT ALL PRIVILEGES ON DATABASE workflow_platform TO workflow_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO workflow_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO workflow_user;
```

### 性能优化
- 调整 `postgresql.conf` 中的内存设置
- 创建适当的索引
- 定期运行 `VACUUM` 和 `ANALYZE`