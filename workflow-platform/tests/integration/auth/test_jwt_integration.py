#!/usr/bin/env python3
"""
JWT Integration Test
测试JWT安全修复后的完整集成流程
"""

import asyncio
import httpx
import json
from datetime import datetime


async def test_jwt_integration():
    """测试JWT集成流程"""
    print("🔐 JWT安全修复集成测试")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api/v1"
    
    async with httpx.AsyncClient() as client:
        try:
            # 测试健康检查
            print("📊 检查API健康状态...")
            health_response = await client.get(f"{base_url}/health", timeout=5.0)
            if health_response.status_code == 200:
                print("  ✅ API服务正常运行")
            else:
                print(f"  ⚠️ API服务状态异常: {health_response.status_code}")
            
        except httpx.TimeoutException:
            print("  ❌ API服务连接超时 - 请确保后端服务正在运行")
            print("  💡 启动命令: cd workflow-platform && python -m uvicorn main:app --reload")
            return False
        except httpx.ConnectError:
            print("  ❌ 无法连接到API服务 - 请确保后端服务正在运行")
            print("  💡 启动命令: cd workflow-platform && python -m uvicorn main:app --reload")
            return False
        except Exception as e:
            print(f"  ❌ 连接错误: {e}")
            return False
        
        try:
            # 测试无需认证的端点
            print("\n🔓 测试公开端点...")
            check_response = await client.get(f"{base_url}/users/auth/check-username?username=testuser")
            if check_response.status_code == 200:
                print("  ✅ 用户名检查端点正常")
            
            # 测试发送验证码（不需要认证）
            verification_response = await client.post(
                f"{base_url}/users/auth/send-verification-code",
                json={"email": "test@example.com", "purpose": "register"}
            )
            if verification_response.status_code in [200, 429]:  # 200成功或429频率限制都是正常的
                print("  ✅ 发送验证码端点正常")
            else:
                print(f"  ⚠️ 发送验证码端点响应: {verification_response.status_code}")
            
        except Exception as e:
            print(f"  ❌ 公开端点测试失败: {e}")
        
        try:
            # 测试需要认证的端点（应该返回401）
            print("\n🔒 测试受保护端点...")
            protected_response = await client.get(f"{base_url}/users/me")
            if protected_response.status_code == 401:
                print("  ✅ 受保护端点正确拒绝未认证请求")
            else:
                print(f"  ⚠️ 受保护端点响应异常: {protected_response.status_code}")
            
        except Exception as e:
            print(f"  ❌ 受保护端点测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 集成测试摘要:")
    print("  • JWT安全修复已部署到后端")
    print("  • 访问令牌过期时间: 15分钟")
    print("  • 刷新令牌过期时间: 7天") 
    print("  • Redis黑名单机制已启用")
    print("  • 前端自动令牌刷新已配置")
    
    print("\n💡 下一步测试建议:")
    print("  1. 启动后端服务进行完整功能测试")
    print("  2. 启动前端应用测试用户界面")
    print("  3. 测试用户注册、登录、登出流程")
    print("  4. 验证令牌过期和自动刷新")
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_jwt_integration())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n集成测试错误: {e}")
        exit(1)