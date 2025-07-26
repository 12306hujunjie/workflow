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
# 加载.env文件中的环境变量
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi
# 从环境变量读取配置，使用默认值作为备用
API_HOST=${API_HOST:-0.0.0.0}
API_PORT=${API_PORT:-8000}
python3 -m uvicorn api_gateway.main:app --reload --host $API_HOST --port $API_PORT