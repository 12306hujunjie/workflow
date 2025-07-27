"""用户API集成测试"""

import asyncio
import random

import pytest
from fastapi import status


@pytest.mark.asyncio
class TestUserAPI:
    """用户API集成测试"""

    async def test_register_login_flow(self, api_client, base_settings):
        """测试完整的注册登录流程"""

        # 1. 注册新用户
        register_response = await api_client.post(
            f"{base_settings.api_v1_prefix}/auth/register",
            json={
                "username": "integrationtest",
                "email": "integration@test.com",
                "password": "Integration@123"
            }
        )

        assert register_response.status_code == status.HTTP_200_OK
        response_data = register_response.json()
        assert response_data["success"] == True
        user_data = response_data["data"]
        assert user_data["username"] == "integrationtest"
        assert user_data["email"] == "integration@test.com"
        user_id = user_data["id"]

        # 2. 登录用户（邮箱服务未接入，用户默认为激活状态）
        login_response = await api_client.post(
            f"{base_settings.api_v1_prefix}/auth/login",
            json={
                "username_or_email": "integrationtest",
                "password": "Integration@123"
            }
        )

        assert login_response.status_code == status.HTTP_200_OK
        login_data = login_response.json()
        assert login_data["success"] == True
        assert "access_token" in login_data["data"]
        assert "refresh_token" in login_data["data"]

    async def test_profile_management(self, api_client, base_settings):
        """测试用户资料管理"""

        # 1. 注册用户
        register_response = await api_client.post(
            f"{base_settings.api_v1_prefix}/auth/register",
            json={
                "username": "profiletest",
                "email": "profile@test.com",
                "password": "Profile@123"
            }
        )

        assert register_response.status_code == status.HTTP_200_OK
        response_data = register_response.json()
        assert response_data["success"] == True
        user_data = response_data["data"]
        user_id = user_data["id"]

        # 2. 获取用户资料（需要认证，这里跳过）
        # 在实际测试中，需要先登录获取token

    async def test_concurrent_registration(self, api_client, base_settings):
        """测试并发注册相同用户名"""

        # 使用随机用户名避免与其他测试冲突
        base_username = f"concurrentuser{random.randint(10000, 99999)}"

        # 创建多个并发注册请求
        tasks = []
        for i in range(5):
            task = api_client.post(
                f"{base_settings.api_v1_prefix}/auth/register",
                json={
                    "username": base_username,
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
                if response.status_code == status.HTTP_200_OK:
                    success_count += 1
                elif response.status_code == 409:  # Conflict
                    conflict_count += 1

        # 应该只有一个成功，其他都是冲突
        assert success_count == 1
        assert conflict_count == 4

    async def test_password_validation(self, api_client, base_settings):
        """测试密码验证规则"""

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
                "expected_status": status.HTTP_200_OK,
                "reason": "有效密码"
            }
        ]

        for i, test_case in enumerate(test_cases):
            response = await api_client.post(
                f"{base_settings.api_v1_prefix}/auth/register",
                json={
                    "username": f"passtest{i}",
                    "email": f"passtest{i}@test.com",
                    "password": test_case["password"]
                }
            )

            assert response.status_code == test_case["expected_status"], \
                f"测试用例失败: {test_case['reason']}"

    async def test_username_validation(self, api_client, base_settings):
        """测试用户名验证规则"""
        test_cases = [
            {
                "username": "ab",  # 太短
                "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
            },
            {
                "username": "a" * 51,  # 太长
                "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
            },
            {
                "username": "user@name",  # 包含特殊字符
                "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
            },
            {
                "username": "valid_user123",  # 有效用户名
                "expected_status": status.HTTP_200_OK
            }
        ]

        for i, test_case in enumerate(test_cases):
            response = await api_client.post(
                f"{base_settings.api_v1_prefix}/auth/register",
                json={
                    "username": test_case["username"],
                    "email": f"usertest{i}@test.com",
                    "password": "Valid@123456"
                }
            )

            assert response.status_code == test_case["expected_status"]

    async def test_email_validation(self, api_client, base_settings):
        """测试邮箱验证规则"""

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
                "expected_status": status.HTTP_200_OK
            }
        ]

        for i, test_case in enumerate(test_cases):
            response = await api_client.post(
                f"{base_settings.api_v1_prefix}/auth/register",
                json={
                    "username": f"emailtest{i}",
                    "email": test_case["email"],
                    "password": "Valid@123456"
                }
            )

            assert response.status_code == test_case["expected_status"]
