#!/usr/bin/env python3
"""API测试脚本"""

import asyncio
import httpx
import json
from typing import Dict, Any


class APITester:
    """API测试类"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
    
    async def test_health_check(self) -> Dict[str, Any]:
        """测试健康检查"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            return {
                "status_code": response.status_code,
                "response": response.json()
            }
    
    async def test_user_registration(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """测试用户注册"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/register",
                json=user_data
            )
            return {
                "status_code": response.status_code,
                "response": response.json()
            }
    
    async def test_user_login(self, login_data: Dict[str, Any]) -> Dict[str, Any]:
        """测试用户登录"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data
            )
            result = {
                "status_code": response.status_code,
                "response": response.json()
            }
            
            # 保存token用于后续测试
            if response.status_code == 200 and "data" in result["response"]:
                data = result["response"]["data"]
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
            
            return result
    
    async def test_get_current_user(self) -> Dict[str, Any]:
        """测试获取当前用户信息"""
        if not self.access_token:
            return {"error": "No access token available"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/users/me",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            return {
                "status_code": response.status_code,
                "response": response.json()
            }
    
    async def test_token_refresh(self) -> Dict[str, Any]:
        """测试token刷新"""
        if not self.refresh_token:
            return {"error": "No refresh token available"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )
            
            result = {
                "status_code": response.status_code,
                "response": response.json()
            }
            
            # 更新token
            if response.status_code == 200 and "data" in result["response"]:
                data = result["response"]["data"]
                self.access_token = data.get("access_token")
            
            return result
    
    async def run_tests(self):
        """运行所有测试"""
        print("=== API测试开始 ===")
        
        # 1. 健康检查
        print("\n1. 测试健康检查...")
        health_result = await self.test_health_check()
        print(f"状态码: {health_result['status_code']}")
        print(f"响应: {json.dumps(health_result['response'], indent=2, ensure_ascii=False)}")
        
        # 2. 用户注册
        print("\n2. 测试用户注册...")
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        register_result = await self.test_user_registration(register_data)
        print(f"状态码: {register_result['status_code']}")
        print(f"响应: {json.dumps(register_result['response'], indent=2, ensure_ascii=False)}")
        
        # 3. 用户登录
        print("\n3. 测试用户登录...")
        login_data = {
            "username": "testuser",
            "password": "TestPassword123!"
        }
        login_result = await self.test_user_login(login_data)
        print(f"状态码: {login_result['status_code']}")
        print(f"响应: {json.dumps(login_result['response'], indent=2, ensure_ascii=False)}")
        
        # 4. 获取当前用户信息
        print("\n4. 测试获取当前用户信息...")
        user_info_result = await self.test_get_current_user()
        print(f"状态码: {user_info_result.get('status_code', 'N/A')}")
        print(f"响应: {json.dumps(user_info_result.get('response', user_info_result), indent=2, ensure_ascii=False)}")
        
        # 5. Token刷新
        print("\n5. 测试Token刷新...")
        refresh_result = await self.test_token_refresh()
        print(f"状态码: {refresh_result.get('status_code', 'N/A')}")
        print(f"响应: {json.dumps(refresh_result.get('response', refresh_result), indent=2, ensure_ascii=False)}")
        
        print("\n=== API测试完成 ===")


async def main():
    """主函数"""
    tester = APITester()
    await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())