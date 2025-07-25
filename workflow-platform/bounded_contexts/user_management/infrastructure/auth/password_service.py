"""密码加密服务"""

import bcrypt
from typing import Tuple


class PasswordService:
    """密码加密服务"""
    
    def __init__(self, rounds: int = 12):
        self.rounds = rounds
    
    def hash_password(self, password: str) -> str:
        """对密码进行哈希加密"""
        # 生成salt并加密密码
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """验证密码是否正确"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """验证密码强度"""
        if len(password) < 8:
            return False, "密码长度至少需要8个字符"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not has_upper:
            return False, "密码需要包含至少一个大写字母"
        if not has_lower:
            return False, "密码需要包含至少一个小写字母"
        if not has_digit:
            return False, "密码需要包含至少一个数字"
        if not has_special:
            return False, "密码需要包含至少一个特殊字符"
        
        return True, "密码强度符合要求"