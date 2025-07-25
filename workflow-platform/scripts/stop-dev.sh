#!/bin/bash

# 停止开发环境脚本

echo "Stopping development environment..."

# 停止Docker容器
echo "Stopping PostgreSQL and Redis..."
docker-compose down

echo "Development environment stopped."