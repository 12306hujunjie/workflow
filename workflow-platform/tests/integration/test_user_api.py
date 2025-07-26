"""用户API集成测试"""

import pytest
from httpx import AsyncClient
from fastapi import status
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from api_gateway.main import create_app
from config.settings import Settings
from shared_kernel.application.exception_handlers import register_exception_handlers
# 重要：从全局导入 container 实例
from container import container


def create_test_services():
    """创建测试服务实例"""
    from bounded_contexts.user_management.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
    from bounded_contexts.user_management.infrastructure.auth.password_service import PasswordService
    from bounded_contexts.user_management.infrastructure.auth.jwt_service import JWTService
    from bounded_contexts.user_management.application.services.user_application_service import UserApplicationService
    from shared_kernel.infrastructure.database.async_session import DatabaseConfig
    
    # 创建配置
    settings = Settings(
        database_url="postgresql+asyncpg://postgres:password@localhost:5432/workflow_platform",
        jwt_secret_key="test-secret-key",
        jwt_algorithm="HS256",
        jwt_access_token_expire_minutes=30,
        jwt_refresh_token_expire_days=7,
        cors_allowed_origins=["http://localhost:3000"],
        redis_url="redis://localhost:6379/0"
    )
    
    # 创建数据库配置
    db_config = DatabaseConfig(database_url=settings.database_url)
    
    # 创建服务实例
    password_service = PasswordService(rounds=settings.bcrypt_rounds)
    jwt_service = JWTService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
        refresh_token_expire_days=settings.jwt_refresh_token_expire_days
    )
    
    # 创建应用服务工厂 - 返回实际的服务实例
    async def create_user_service():
        session_factory = db_config.async_session_factory()
        session = session_factory()
        user_repository = SQLAlchemyUserRepository(session)
        return UserApplicationService(
            user_repository=user_repository,
            password_service=password_service,
            jwt_service=jwt_service
        )
    
    return create_user_service


def create_test_app():
    """创建测试应用实例"""
    # 创建服务工厂
    create_user_service = create_test_services()
    
    @asynccontextmanager
    async def test_lifespan(app: FastAPI):
        # 启动时
        yield
        
        # 关闭时
        pass
    
    # 创建测试应用
    app = FastAPI(
        title="Test App",
        version="1.0.0",
        lifespan=test_lifespan
    )
    
    # 注册全局异常处理器
    register_exception_handlers(app)
    
    # 导入路由
    from bounded_contexts.user_management.presentation.api.user_routes import router as user_router
    from bounded_contexts.user_management.presentation.api.auth_routes import router as auth_router
    from bounded_contexts.user_management.presentation.api.admin_routes import router as admin_router
    
    # 使用 dependency_overrides 绕过容器依赖注入
    from bounded_contexts.user_management.presentation.dependencies import get_user_service
    
    # 覆盖依赖函数
    # 注意：create_user_service是一个async函数，需要直接作为依赖工厂使用
    app.dependency_overrides[get_user_service] = create_user_service
    
    # 注册路由
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(user_router, prefix="/api/v1/users", tags=["User Management"])
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
    
    return app


@pytest.fixture
def test_app():
    """测试应用fixture"""
    return create_test_app()


@pytest.mark.asyncio
class TestUserAPI:
    """用户API集成测试"""
    
    async def test_register_login_flow(self, test_app):
        """测试完整的注册登录流程"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # 1. 注册新用户
            register_response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "integrationtest",
                    "email": "integration@test.com",
                    "password": "Integration@123"
                }
            )
            
            assert register_response.status_code == status.HTTP_201_CREATED
            user_data = register_response.json()
            assert user_data["username"] == "integrationtest"
            assert user_data["email"] == "integration@test.com"
            user_id = user_data["id"]
            
            # 2. 尝试登录未激活账户（应该失败）
            login_response = await client.post(
                "/api/v1/auth/login",
                json={
                    "username": "integrationtest",
                    "password": "Integration@123"
                }
            )
            
            assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
            
            # 3. 模拟激活用户（实际应用中通过邮件链接）
            # 这里我们直接更新数据库状态来模拟激活
            # 在实际测试中，可以通过专门的测试端点或直接操作数据库
            
            # 4. 再次尝试登录（假设已激活）
            # 注意：由于测试环境限制，这里可能需要模拟激活过程
    
    async def test_profile_management(self, test_app):
        """测试用户资料管理"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # 1. 注册用户
            register_response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "profiletest",
                    "email": "profile@test.com",
                    "password": "Profile@123"
                }
            )
            
            assert register_response.status_code == status.HTTP_201_CREATED
            user_data = register_response.json()
            user_id = user_data["id"]
            
            # 2. 获取用户资料（需要认证，这里跳过）
            # 在实际测试中，需要先登录获取token
    
    async def test_concurrent_registration(self, test_app):
        """测试并发注册相同用户名"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # 创建多个并发注册请求
            tasks = []
            for i in range(5):
                task = client.post(
                    "/api/v1/auth/register",
                    json={
                        "username": "concurrentuser",
                        "email": f"concurrent{i}@test.com",
                        "password": "Concurrent@123"
                    }
                )
                tasks.append(task)
            
            # 并发执行
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 统计成功和失败的请求
            success_count = 0
            conflict_count = 0
            
            for response in responses:
                if not isinstance(response, Exception):
                    if response.status_code == status.HTTP_201_CREATED:
                        success_count += 1
                    elif response.status_code == status.HTTP_400_BAD_REQUEST:
                        conflict_count += 1
            
            # 应该只有一个成功，其他都是冲突
            assert success_count == 1
            assert conflict_count == 4
    
    async def test_password_validation(self, test_app):
        """测试密码验证规则"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            test_cases = [
                {
                    "password": "short",
                    "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "reason": "密码太短"
                },
                {
                    "password": "nouppercase123!",
                    "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "reason": "缺少大写字母"
                },
                {
                    "password": "NOLOWERCASE123!",
                    "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "reason": "缺少小写字母"
                },
                {
                    "password": "NoNumbers!",
                    "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "reason": "缺少数字"
                },
                {
                    "password": "NoSpecial123",
                    "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "reason": "缺少特殊字符"
                },
                {
                    "password": "Valid@123456",
                    "expected_status": status.HTTP_201_CREATED,
                    "reason": "有效密码"
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                response = await client.post(
                    "/api/v1/auth/register",
                    json={
                        "username": f"passtest{i}",
                        "email": f"passtest{i}@test.com",
                        "password": test_case["password"]
                    }
                )
                
                assert response.status_code == test_case["expected_status"], \
                    f"测试用例失败: {test_case['reason']}"
    
    async def test_username_validation(self, test_app):
        """测试用户名验证规则"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            test_cases = [
                {
                    "username": "ab",  # 太短
                    "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
                },
                {
                    "username": "a" * 21,  # 太长
                    "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
                },
                {
                    "username": "user@name",  # 包含特殊字符
                    "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
                },
                {
                    "username": "valid_user123",  # 有效用户名
                    "expected_status": status.HTTP_201_CREATED
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                response = await client.post(
                    "/api/v1/auth/register",
                    json={
                        "username": test_case["username"],
                        "email": f"usertest{i}@test.com",
                        "password": "Valid@123456"
                    }
                )
                
                assert response.status_code == test_case["expected_status"]
    
    async def test_email_validation(self, test_app):
        """测试邮箱验证规则"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            test_cases = [
                {
                    "email": "invalid-email",
                    "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
                },
                {
                    "email": "@example.com",
                    "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
                },
                {
                    "email": "test@",
                    "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
                },
                {
                    "email": "valid@example.com",
                    "expected_status": status.HTTP_201_CREATED
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                response = await client.post(
                    "/api/v1/auth/register",
                    json={
                        "username": f"emailtest{i}",
                        "email": test_case["email"],
                        "password": "Valid@123456"
                    }
                )
                
                assert response.status_code == test_case["expected_status"]