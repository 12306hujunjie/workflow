"""用户注册测试"""

import pytest
from httpx import AsyncClient
from fastapi import status

from api_gateway.main import app


@pytest.mark.asyncio
async def test_register_user_success():
    """测试成功注册用户"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "Test@123456"
            }
        )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["status"] == "pending_verification"
    assert data["role"] == "user"


@pytest.mark.asyncio
async def test_register_user_duplicate_username():
    """测试重复用户名注册"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 第一次注册
        await client.post(
            "/api/v1/users/register",
            json={
                "username": "duplicate",
                "email": "duplicate1@example.com",
                "password": "Test@123456"
            }
        )
        
        # 尝试使用相同用户名注册
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "duplicate",
                "email": "duplicate2@example.com",
                "password": "Test@123456"
            }
        )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "用户名已存在" in response.json()["message"]


@pytest.mark.asyncio
async def test_register_user_weak_password():
    """测试弱密码注册"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "weakpass",
                "email": "weak@example.com",
                "password": "weak"
            }
        )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_register_user_invalid_email():
    """测试无效邮箱注册"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users/register",
            json={
                "username": "invalidemail",
                "email": "invalid-email",
                "password": "Test@123456"
            }
        )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY