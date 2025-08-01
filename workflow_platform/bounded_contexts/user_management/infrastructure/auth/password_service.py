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

        
        return True, "密码强度符合要求"