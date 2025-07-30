"""
Profile API修复验证测试

这个测试文件专门验证我们修复的profile API问题：
1. 前端first_name/last_name到后端display_name的转换
2. UserProfileResponse验证修复
3. JWT token认证修复
"""

import pytest
from fastapi import status


@pytest.mark.asyncio
class TestProfileAPIFix:
    """Profile API修复验证测试"""

    async def test_jwt_authentication_flow(self, api_client, base_settings):
        """测试JWT认证流程 - 修复403错误"""
        
        # 1. 注册用户
        register_data = {
            "username": "jwttest",
            "email": "jwttest@example.com",
            "password": "JwtTest123@"
        }
        
        register_response = await api_client.post(
            f"{base_settings.api_v1_prefix}/auth/register",
            json=register_data
        )
        
        assert register_response.status_code == status.HTTP_200_OK
        register_result = register_response.json()
        assert register_result["success"] == True
        
        # 2. 登录获取JWT token
        login_response = await api_client.post(
            f"{base_settings.api_v1_prefix}/auth/login",
            json={
                "username_or_email": "jwttest",
                "password": "JwtTest123@"
            }
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        login_result = login_response.json()
        assert login_result["success"] == True
        
        access_token = login_result["data"]["access_token"]
        assert access_token is not None
        assert len(access_token) > 50  # JWT token should be substantial
        
        # 3. 使用token访问受保护的API - 不应该返回403
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = await api_client.get(
            f"{base_settings.api_v1_prefix}/users/me",
            headers=headers
        )
        
        assert profile_response.status_code == status.HTTP_200_OK
        profile_result = profile_response.json()
        assert profile_result["success"] == True
        assert profile_result["data"]["username"] == "jwttest"

    async def test_profile_data_validation_fix(self, api_client, base_settings):
        """测试Profile数据验证修复 - UserProfileResponse.model_validate错误"""
        
        # 设置认证
        user_data = await self._create_authenticated_user(api_client, base_settings, "validationtest")
        headers = {"Authorization": f"Bearer {user_data['token']}"}
        
        # 测试各种profile数据格式，确保不出现model_validate错误
        test_cases = [
            {
                "name": "完整资料",
                "data": {
                    "display_name": "验证测试用户",
                    "bio": "这是profile验证测试的个人简介",
                    "timezone": "Asia/Shanghai",
                    "language": "zh-CN"
                }
            },
            {
                "name": "最小资料",
                "data": {
                    "display_name": "最小用户"
                }
            },
            {
                "name": "部分资料",
                "data": {
                    "display_name": "部分用户",
                    "timezone": "UTC"
                }
            },
            {
                "name": "空字符串处理",
                "data": {
                    "display_name": "",
                    "bio": "",
                    "timezone": "Asia/Tokyo",
                    "language": "ja-JP"
                }
            }
        ]
        
        for test_case in test_cases:
            # 更新profile
            update_response = await api_client.put(
                f"{base_settings.api_v1_prefix}/users/me/profile",
                json=test_case["data"],
                headers=headers
            )
            
            # 不应该出现422或500错误
            assert update_response.status_code == status.HTTP_200_OK, \
                f"测试用例'{test_case['name']}'失败: {update_response.status_code}"
            
            update_result = update_response.json()
            assert update_result["success"] == True, \
                f"测试用例'{test_case['name']}'返回success=False"
            
            # 验证数据正确保存
            if test_case["data"].get("display_name"):
                assert update_result["data"]["profile"]["display_name"] == test_case["data"]["display_name"]

    async def test_profile_field_mapping_simulation(self, api_client, base_settings):
        """测试模拟前端字段映射 - first_name/last_name转display_name"""
        
        # 设置认证
        user_data = await self._create_authenticated_user(api_client, base_settings, "mappingtest")
        headers = {"Authorization": f"Bearer {user_data['token']}"}
        
        # 模拟前端修复后发送的数据格式（已转换为display_name）
        frontend_fixed_data = {
            "display_name": "张三",  # 前端已将"张"+"三"合并
            "bio": "这是前端修复后的数据格式测试",
            "timezone": "Asia/Shanghai",
            "language": "zh-CN"
        }
        
        update_response = await api_client.put(
            f"{base_settings.api_v1_prefix}/users/me/profile",
            json=frontend_fixed_data,
            headers=headers
        )
        
        assert update_response.status_code == status.HTTP_200_OK
        update_result = update_response.json()
        assert update_result["success"] == True
        assert update_result["data"]["profile"]["display_name"] == "张三"
        
        # 验证数据持久化
        get_response = await api_client.get(
            f"{base_settings.api_v1_prefix}/users/me",
            headers=headers
        )
        
        assert get_response.status_code == status.HTTP_200_OK
        get_result = get_response.json()
        assert get_result["data"]["profile"]["display_name"] == "张三"

    async def test_error_handling_improvements(self, api_client, base_settings):
        """测试错误处理改进 - 确保不再出现模糊的422错误"""
        
        # 设置认证
        user_data = await self._create_authenticated_user(api_client, base_settings, "errortest")
        headers = {"Authorization": f"Bearer {user_data['token']}"}
        
        # 测试各种可能导致错误的情况
        error_test_cases = [
            {
                "name": "超长display_name",
                "data": {"display_name": "a" * 200},  # 超过100字符限制
                "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
            },
            {
                "name": "超长bio",
                "data": {"bio": "a" * 600},  # 超过500字符限制
                "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
            },
            {
                "name": "无效timezone",
                "data": {"timezone": "a" * 60},  # 超过50字符限制
                "expected_status": status.HTTP_422_UNPROCESSABLE_ENTITY
            }
        ]
        
        for test_case in error_test_cases:
            error_response = await api_client.put(
                f"{base_settings.api_v1_prefix}/users/me/profile",
                json=test_case["data"],
                headers=headers
            )
            
            assert error_response.status_code == test_case["expected_status"], \
                f"错误测试用例'{test_case['name']}'应该返回{test_case['expected_status']}"
            
            if error_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
                error_result = error_response.json()
                # 错误信息应该清晰，不应该是"Input should be a valid dictionary"
                assert "model_type" not in str(error_result), \
                    f"仍然出现model_validate错误: {error_result}"

    async def test_no_authentication_errors(self, api_client, base_settings):
        """测试无认证访问的错误处理"""
        
        # 不提供Authorization header
        no_auth_response = await api_client.put(
            f"{base_settings.api_v1_prefix}/users/me/profile",
            json={"display_name": "测试"}
        )
        
        assert no_auth_response.status_code == status.HTTP_403_FORBIDDEN
        
        # 提供无效token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        invalid_auth_response = await api_client.put(
            f"{base_settings.api_v1_prefix}/users/me/profile",
            json={"display_name": "测试"},
            headers=invalid_headers
        )
        
        assert invalid_auth_response.status_code == status.HTTP_403_FORBIDDEN

    async def _create_authenticated_user(self, api_client, base_settings, username_prefix):
        """辅助方法：创建已认证的用户"""
        
        # 注册
        register_response = await api_client.post(
            f"{base_settings.api_v1_prefix}/auth/register",
            json={
                "username": username_prefix,
                "email": f"{username_prefix}@example.com",
                "password": "Test123@"
            }
        )
        
        assert register_response.status_code == status.HTTP_200_OK
        
        # 登录
        login_response = await api_client.post(
            f"{base_settings.api_v1_prefix}/auth/login",
            json={
                "username_or_email": username_prefix,
                "password": "Test123@"
            }
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        login_result = login_response.json()
        
        return {
            "user_id": register_response.json()["data"]["id"],
            "token": login_result["data"]["access_token"]
        }