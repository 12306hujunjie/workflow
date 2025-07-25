"""认证服务单元测试"""

import pytest
from datetime import datetime, timedelta
import jwt

from bounded_contexts.user_management.infrastructure.auth.password_service import PasswordService
from bounded_contexts.user_management.infrastructure.auth.jwt_service import JWTService


class TestPasswordService:
    """密码服务测试"""
    
    def test_hash_password(self):
        """测试密码哈希"""
        service = PasswordService()
        password = "Test@123456"
        
        hashed = service.hash_password(password)
        
        # 验证哈希值不同于原密码
        assert hashed != password
        # 验证哈希值以bcrypt前缀开始
        assert hashed.startswith("$2b$")
    
    def test_verify_password_correct(self):
        """测试验证正确密码"""
        service = PasswordService()
        password = "Test@123456"
        
        hashed = service.hash_password(password)
        
        # 验证正确密码
        assert service.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """测试验证错误密码"""
        service = PasswordService()
        password = "Test@123456"
        wrong_password = "Wrong@123456"
        
        hashed = service.hash_password(password)
        
        # 验证错误密码
        assert service.verify_password(wrong_password, hashed) is False
    
    def test_hash_password_different_each_time(self):
        """测试同一密码生成不同哈希值"""
        service = PasswordService()
        password = "Test@123456"
        
        hash1 = service.hash_password(password)
        hash2 = service.hash_password(password)
        
        # 验证两次哈希值不同
        assert hash1 != hash2
        
        # 但都能验证原密码
        assert service.verify_password(password, hash1) is True
        assert service.verify_password(password, hash2) is True


class TestJWTService:
    """JWT服务测试"""
    
    def test_create_access_token(self):
        """测试创建访问令牌"""
        service = JWTService(secret_key="test-secret", algorithm="HS256")
        user_id = "test-user-id"
        
        token = service.create_access_token(user_id=user_id)
        
        # 解码验证
        payload = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload
    
    def test_create_refresh_token(self):
        """测试创建刷新令牌"""
        service = JWTService(secret_key="test-secret", algorithm="HS256")
        user_id = "test-user-id"
        
        token = service.create_refresh_token(user_id=user_id)
        
        # 解码验证
        payload = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload
    
    def test_create_access_token_with_custom_expiry(self):
        """测试创建自定义过期时间的访问令牌"""
        service = JWTService(
            secret_key="test-secret",
            algorithm="HS256",
            access_token_expire_minutes=60
        )
        user_id = "test-user-id"
        
        token = service.create_access_token(user_id=user_id)
        payload = jwt.decode(token, "test-secret", algorithms=["HS256"])
        
        # 验证过期时间约为60分钟后
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        diff = exp_time - iat_time
        
        # 允许几秒的误差
        assert 59 <= diff.total_seconds() / 60 <= 61
    
    def test_verify_token_valid(self):
        """测试验证有效令牌"""
        service = JWTService(secret_key="test-secret", algorithm="HS256")
        user_id = "test-user-id"
        
        token = service.create_access_token(user_id=user_id)
        payload = service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
    
    def test_verify_token_expired(self):
        """测试验证过期令牌"""
        service = JWTService(
            secret_key="test-secret",
            algorithm="HS256",
            access_token_expire_minutes=-1  # 立即过期
        )
        user_id = "test-user-id"
        
        token = service.create_access_token(user_id=user_id)
        
        # 验证过期令牌
        payload = service.verify_token(token)
        assert payload is None
    
    def test_verify_token_invalid_signature(self):
        """测试验证无效签名的令牌"""
        service1 = JWTService(secret_key="secret1", algorithm="HS256")
        service2 = JWTService(secret_key="secret2", algorithm="HS256")
        
        # 使用service1创建令牌
        token = service1.create_access_token(user_id="test-user-id")
        
        # 使用service2验证（不同密钥）
        payload = service2.verify_token(token)
        assert payload is None
    
    def test_verify_token_malformed(self):
        """测试验证格式错误的令牌"""
        service = JWTService(secret_key="test-secret", algorithm="HS256")
        
        # 验证格式错误的令牌
        payload = service.verify_token("invalid.token.format")
        assert payload is None
        
        payload = service.verify_token("not-a-jwt-token")
        assert payload is None
        
        payload = service.verify_token("")
        assert payload is None
    
    def test_get_user_id_from_token(self):
        """测试从令牌获取用户ID"""
        service = JWTService(secret_key="test-secret", algorithm="HS256")
        user_id = "test-user-id"
        
        token = service.create_access_token(user_id=user_id)
        extracted_user_id = service.get_user_id_from_token(token)
        
        assert extracted_user_id == user_id
    
    def test_get_user_id_from_invalid_token(self):
        """测试从无效令牌获取用户ID"""
        service = JWTService(secret_key="test-secret", algorithm="HS256")
        
        # 从无效令牌获取用户ID
        user_id = service.get_user_id_from_token("invalid-token")
        assert user_id is None
    
    def test_refresh_access_token(self):
        """测试刷新访问令牌"""
        service = JWTService(secret_key="test-secret", algorithm="HS256")
        user_id = "test-user-id"
        
        # 创建刷新令牌
        refresh_token = service.create_refresh_token(user_id=user_id)
        
        # 使用刷新令牌获取新的访问令牌
        new_access_token = service.refresh_access_token(refresh_token)
        
        assert new_access_token is not None
        
        # 验证新令牌
        payload = service.verify_token(new_access_token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
    
    def test_refresh_access_token_with_access_token(self):
        """测试使用访问令牌刷新（应该失败）"""
        service = JWTService(secret_key="test-secret", algorithm="HS256")
        user_id = "test-user-id"
        
        # 创建访问令牌
        access_token = service.create_access_token(user_id=user_id)
        
        # 尝试使用访问令牌刷新
        new_token = service.refresh_access_token(access_token)
        assert new_token is None