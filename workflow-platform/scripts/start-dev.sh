#!/bin/bash

# 开发环境启动脚本

echo "Starting development environment..."

# 检查.env文件是否存在
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file to configure your environment"
    exit 1
fi

# 启动数据库和Redis
echo "Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis

# 等待服务启动
echo "Waiting for services to be ready..."
sleep 5

# 检查PostgreSQL是否就绪
until docker-compose exec -T postgres pg_isready -U postgres; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

# 运行数据库迁移
echo "Running database migrations..."
docker-compose exec -T postgres psql -U postgres -d workflow_platform -f /docker-entrypoint-initdb.d/user_management.sql || true

# 启动应用
echo "Starting FastAPI application..."
uvicorn api_gateway.main:app --reload --host 0.0.0.0 --port 8000