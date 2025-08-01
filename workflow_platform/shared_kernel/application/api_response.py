"""Unified API response format for all endpoints."""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ApiResponse(BaseModel):
    """Standard API response format."""
    
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime
    request_id: Optional[str] = None
    
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    @classmethod
    def success_response(
        cls,
        data: Any = None,
        message: str = "操作成功",
        request_id: Optional[str] = None
    ) -> "ApiResponse":
        """Create a successful response."""
        return cls(
            success=True,
            message=message,
            data=data,
            timestamp=datetime.utcnow(),
            request_id=request_id
        )
    
    @classmethod
    def error_response(
        cls,
        message: str = "操作失败",
        errors: Optional[List[Dict[str, Any]]] = None,
        request_id: Optional[str] = None
    ) -> "ApiResponse":
        """Create an error response."""
        return cls(
            success=False,
            message=message,
            errors=errors,
            timestamp=datetime.utcnow(),
            request_id=request_id
        )


class PaginatedResponse(BaseModel):
    """Paginated response format."""
    
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls,
        items: List[Any],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse":
        """Create a paginated response."""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class ValidationErrorDetail(BaseModel):
    """Validation error detail."""
    
    field: str
    message: str
    code: str
    value: Optional[Any] = None


class ErrorCode:
    """Standard error codes."""
    
    # Authentication & Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    
    # User Management
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    USERNAME_ALREADY_EXISTS = "USERNAME_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"
    ACCOUNT_BANNED = "ACCOUNT_BANNED"
    EMAIL_NOT_VERIFIED = "EMAIL_NOT_VERIFIED"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # System
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Business Logic
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"