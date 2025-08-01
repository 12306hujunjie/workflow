"""Custom exceptions for the application."""
from typing import Any, Dict, List, Optional


class BaseApplicationException(Exception):
    """Base exception for all application exceptions."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(BaseApplicationException):
    """Validation error exception."""
    
    def __init__(
        self,
        message: str = "验证失败",
        field_errors: Optional[List[Dict[str, Any]]] = None,
        error_code: str = "VALIDATION_ERROR"
    ):
        details = {"field_errors": field_errors or []}
        super().__init__(message, error_code, details, 400)


class AuthenticationException(BaseApplicationException):
    """Authentication error exception."""
    
    def __init__(
        self,
        message: str = "认证失败",
        error_code: str = "UNAUTHORIZED"
    ):
        super().__init__(message, error_code, status_code=401)


class AuthorizationException(BaseApplicationException):
    """Authorization error exception."""
    
    def __init__(
        self,
        message: str = "权限不足",
        error_code: str = "FORBIDDEN"
    ):
        super().__init__(message, error_code, status_code=403)


class NotFoundException(BaseApplicationException):
    """Resource not found exception."""
    
    def __init__(
        self,
        message: str = "资源未找到",
        error_code: str = "RESOURCE_NOT_FOUND",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        super().__init__(message, error_code, details, 404)


class ConflictException(BaseApplicationException):
    """Resource conflict exception."""
    
    def __init__(
        self,
        message: str = "资源冲突",
        error_code: str = "DUPLICATE_RESOURCE",
        conflicting_field: Optional[str] = None,
        conflicting_value: Optional[str] = None
    ):
        details = {}
        if conflicting_field:
            details["conflicting_field"] = conflicting_field
        if conflicting_value:
            details["conflicting_value"] = conflicting_value
        super().__init__(message, error_code, details, 409)


class BusinessLogicException(BaseApplicationException):
    """Business logic error exception."""
    
    def __init__(
        self,
        message: str = "业务逻辑错误",
        error_code: str = "OPERATION_NOT_ALLOWED"
    ):
        super().__init__(message, error_code, status_code=422)


class TokenException(AuthenticationException):
    """Token related exceptions."""
    
    def __init__(
        self,
        message: str = "令牌无效",
        error_code: str = "TOKEN_INVALID"
    ):
        super().__init__(message, error_code)


class TokenExpiredException(TokenException):
    """Token expired exception."""
    
    def __init__(self, message: str = "令牌已过期"):
        super().__init__(message, "TOKEN_EXPIRED")


# User Management Specific Exceptions
class UserNotFoundException(NotFoundException):
    """User not found exception."""
    
    def __init__(self, user_id: Optional[str] = None, username: Optional[str] = None):
        message = "用户未找到"
        details = {}
        if user_id:
            details["user_id"] = user_id
        if username:
            details["username"] = username
        super().__init__(message, "USER_NOT_FOUND", "user", user_id or username)


class UserAlreadyExistsException(ConflictException):
    """User already exists exception."""
    
    def __init__(self, field: str, value: str):
        message = f"用户{field}已存在"
        error_code = "EMAIL_ALREADY_EXISTS" if field == "email" else "USERNAME_ALREADY_EXISTS"
        super().__init__(message, error_code, field, value)


class InvalidCredentialsException(AuthenticationException):
    """Invalid credentials exception."""
    
    def __init__(self, message: str = "用户名或密码错误"):
        super().__init__(message, "INVALID_CREDENTIALS")


class AccountDisabledException(AuthenticationException):
    """Account disabled exception."""
    
    def __init__(self, message: str = "账户已被禁用"):
        super().__init__(message, "ACCOUNT_DISABLED")


class AccountBannedException(AuthenticationException):
    """Account banned exception."""
    
    def __init__(self, message: str = "账户已被封禁"):
        super().__init__(message, "ACCOUNT_BANNED")


class EmailNotVerifiedException(AuthenticationException):
    """Email not verified exception."""
    
    def __init__(self, message: str = "邮箱未验证"):
        super().__init__(message, "EMAIL_NOT_VERIFIED")