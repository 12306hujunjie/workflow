.PHONY: help install test test-unit test-integration coverage lint format clean run migrate docker-up docker-down

help: ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装依赖
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test: ## 运行所有测试
	pytest -v

test-unit: ## 运行单元测试
	pytest tests/unit -v

test-integration: ## 运行集成测试
	pytest tests/integration -v

coverage: ## 运行测试并生成覆盖率报告
	pytest --cov=. --cov-report=html --cov-report=term

lint: ## 运行代码检查
	flake8 .
	mypy .
	black --check .
	isort --check-only .

format: ## 格式化代码
	black .
	isort .

clean: ## 清理临时文件
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

run: ## 运行开发服务器
	@if [ -f .env ]; then export $$(grep -v '^#' .env | xargs); fi && \
	uvicorn api_gateway.main:app --reload --host $${API_HOST:-0.0.0.0} --port $${API_PORT:-8000}

migrate: ## 运行数据库迁移
	docker-compose exec -T postgres psql -U postgres -d workflow_platform -f /docker-entrypoint-initdb.d/user_management.sql

docker-up: ## 启动Docker服务
	docker-compose up -d

docker-down: ## 停止Docker服务
	docker-compose down

docker-logs: ## 查看Docker日志
	docker-compose logs -f

init: ## 初始化项目
	python init.py

freeze: ## 导出依赖
	pip freeze > requirements.txt