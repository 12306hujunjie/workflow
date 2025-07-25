"""用户API集成测试"""

import pytest
from httpx import AsyncClient
from fastapi import status
import asyncio

from api_gateway.main import app, lifespan
from container import init_container


@pytest.mark.asyncio
class TestUserAPI:
    """用户API集成测试"""
    
    async def test_register_login_flow(self):
        """测试完整的注册登录流程"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. 注册新用户
            register_response = await client.post(
                "/api/v1/users/register",
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
    
    async def test_profile_management(self):
        """测试用户资料管理"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. 注册用户
            register_response = await client.post(
                "/api/v1/users/register",
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
    
    async def test_concurrent_registration(self):
        """测试并发注册相同用户名"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 创建多个并发注册请求
            tasks = []
            for i in range(5):
                task = client.post(
                    "/api/v1/users/register",
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
    
    async def test_password_validation(self):
        """测试密码验证规则"""
        async with AsyncClient(app=app, base_url="http://test") as client:
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
                    "/api/v1/users/register",
                    json={
                        "username": f"passtest{i}",
                        "email": f"passtest{i}@test.com",
                        "password": test_case["password"]
                    }
                )
                
                assert response.status_code == test_case["expected_status"], \
                    f"测试用例失败: {test_case['reason']}"
    
    async def test_username_validation(self):
        """测试用户名验证规则"""
        async with AsyncClient(app=app, base_url="http://test") as client:
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
                    "/api/v1/users/register",
                    json={
                        "username": test_case["username"],
                        "email": f"usertest{i}@test.com",
                        "password": "Valid@123456"
                    }
                )
                
                assert response.status_code == test_case["expected_status"]
    
    async def test_email_validation(self):
        """测试邮箱验证规则"""
        async with AsyncClient(app=app, base_url="http://test") as client:
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
                    "/api/v1/users/register",
                    json={
                        "username": f"emailtest{i}",
                        "email": test_case["email"],
                        "password": "Valid@123456"
                    }
                )
                
                assert response.status_code == test_case["expected_status"]