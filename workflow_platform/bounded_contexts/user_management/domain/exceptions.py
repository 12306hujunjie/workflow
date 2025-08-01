"""用户管理领域异常"""

from typing import Optional


class UserDomainError(Exception):
    """用户领域基础异常"""
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.code = code


# TODO: 领域层异常暂时保留但不使用，等架构重构时再决定是否采用纯DDD异常模式
# 当前实现直接在应用层使用应用异常，避免过度设计

class InvalidPasswordError(UserDomainError):
    """无效密码异常 - 纯领域概念"""
    def __init__(self, message: str):
        super().__init__(message, "INVALID_PASSWORD")


class InvalidTokenError(UserDomainError):
    """无效令牌异常 - 纯领域概念"""
    def __init__(self, message: str = "无效的令牌"):
        super().__init__(message, "INVALID_TOKEN")