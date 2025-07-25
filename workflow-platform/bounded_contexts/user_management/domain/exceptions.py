"""用户管理领域异常"""

from typing import Optional


class UserDomainError(Exception):
    """用户领域基础异常"""
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.code = code


class UserNotFoundError(UserDomainError):
    """用户不存在异常"""
    def __init__(self, identifier: str):
        super().__init__(f"用户不存在: {identifier}", "USER_NOT_FOUND")


class UserAlreadyExistsError(UserDomainError):
    """用户已存在异常"""
    def __init__(self, message: str = "用户已存在"):
        super().__init__(message, "USER_ALREADY_EXISTS")


class InvalidCredentialsError(UserDomainError):
    """无效凭证异常"""
    def __init__(self, message: str = "用户名或密码错误"):
        super().__init__(message, "INVALID_CREDENTIALS")


class UserNotActiveError(UserDomainError):
    """用户未激活异常"""
    def __init__(self, message: str = "用户账户未激活"):
        super().__init__(message, "USER_NOT_ACTIVE")


class UserSuspendedError(UserDomainError):
    """用户已暂停异常"""
    def __init__(self, message: str = "用户账户已暂停"):
        super().__init__(message, "USER_SUSPENDED")


class InvalidPasswordError(UserDomainError):
    """无效密码异常"""
    def __init__(self, message: str):
        super().__init__(message, "INVALID_PASSWORD")


class InvalidTokenError(UserDomainError):
    """无效令牌异常"""
    def __init__(self, message: str = "无效的令牌"):
        super().__init__(message, "INVALID_TOKEN")