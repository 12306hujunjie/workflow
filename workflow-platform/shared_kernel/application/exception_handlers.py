"""Global exception handlers for FastAPI."""
import logging
import traceback
from typing import Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .exceptions import BaseApplicationException
from .api_response import ApiResponse, ValidationErrorDetail, ErrorCode

logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    """Get request ID from request headers or generate one."""
    return request.headers.get("X-Request-ID", "unknown")


async def application_exception_handler(
    request: Request, 
    exc: BaseApplicationException
) -> JSONResponse:
    """Handle custom application exceptions."""
    request_id = get_request_id(request)
    
    logger.warning(
        f"Application exception: {exc.error_code} - {exc.message}",
        extra={
            "request_id": request_id,
            "error_code": exc.error_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    errors = [{
        "code": exc.error_code,
        "message": exc.message,
        "details": exc.details
    }]
    
    response = ApiResponse.error_response(
        message=exc.message,
        errors=errors,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(mode='json')
    )


async def http_exception_handler(
    request: Request, 
    exc: HTTPException
) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    request_id = get_request_id(request)
    
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    # Map common HTTP status codes to error codes
    error_code_map = {
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.RESOURCE_NOT_FOUND,
        422: ErrorCode.VALIDATION_ERROR,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE
    }
    
    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
    
    errors = [{
        "code": error_code,
        "message": str(exc.detail),
        "details": {"status_code": exc.status_code}
    }]
    
    response = ApiResponse.error_response(
        message=str(exc.detail),
        errors=errors,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(mode='json')
    )


async def request_validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI request validation exceptions."""
    request_id = get_request_id(request)
    
    logger.warning(
        f"Request validation exception: {len(exc.errors())} errors",
        extra={
            "request_id": request_id,
            "errors": exc.errors(),
            "path": request.url.path,
            "method": request.method
        }
    )
    
    # Convert FastAPI validation errors to our format
    validation_errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        validation_errors.append(ValidationErrorDetail(
            field=field,
            message=error["msg"],
            code=error["type"],
            value=error.get("input")
        ).model_dump())
    
    errors = [{
        "code": ErrorCode.VALIDATION_ERROR,
        "message": "请求参数验证失败",
        "details": {"field_errors": validation_errors}
    }]
    
    response = ApiResponse.error_response(
        message="请求参数验证失败",
        errors=errors,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=422,
        content=response.model_dump(mode='json')
    )


async def validation_exception_handler(
    request: Request, 
    exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic validation exceptions."""
    request_id = get_request_id(request)
    
    logger.warning(
        f"Validation exception: {len(exc.errors())} errors",
        extra={
            "request_id": request_id,
            "errors": exc.errors(),
            "path": request.url.path,
            "method": request.method
        }
    )
    
    # Convert Pydantic errors to our format
    validation_errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        validation_errors.append(ValidationErrorDetail(
            field=field,
            message=error["msg"],
            code=error["type"],
            value=error.get("input")
        ).model_dump())
    
    errors = [{
        "code": ErrorCode.VALIDATION_ERROR,
        "message": "请求参数验证失败",
        "details": {"field_errors": validation_errors}
    }]
    
    response = ApiResponse.error_response(
        message="请求参数验证失败",
        errors=errors,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=422,
        content=response.model_dump(mode='json')
    )


async def integrity_error_handler(
    request: Request, 
    exc: IntegrityError
) -> JSONResponse:
    """Handle SQLAlchemy integrity constraint violations."""
    request_id = get_request_id(request)
    
    logger.error(
        f"Database integrity error: {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    # Try to extract meaningful error message
    error_message = "数据完整性约束违反"
    error_code = ErrorCode.DUPLICATE_RESOURCE
    
    if "UNIQUE constraint failed" in str(exc.orig):
        error_message = "数据已存在，违反唯一性约束"
    elif "FOREIGN KEY constraint failed" in str(exc.orig):
        error_message = "外键约束违反"
        error_code = ErrorCode.VALIDATION_ERROR
    
    errors = [{
        "code": error_code,
        "message": error_message,
        "details": {"database_error": str(exc.orig)}
    }]
    
    response = ApiResponse.error_response(
        message=error_message,
        errors=errors,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=409,
        content=response.model_dump(mode='json')
    )


async def sqlalchemy_error_handler(
    request: Request, 
    exc: SQLAlchemyError
) -> JSONResponse:
    """Handle general SQLAlchemy errors."""
    request_id = get_request_id(request)
    
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    errors = [{
        "code": ErrorCode.INTERNAL_ERROR,
        "message": "数据库操作失败",
        "details": {"error_type": type(exc).__name__}
    }]
    
    response = ApiResponse.error_response(
        message="数据库操作失败",
        errors=errors,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=500,
        content=response.model_dump(mode='json')
    )


async def general_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """Handle all other unhandled exceptions."""
    request_id = get_request_id(request)
    
    logger.error(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    errors = [{
        "code": ErrorCode.INTERNAL_ERROR,
        "message": "服务器内部错误",
        "details": {
            "error_type": type(exc).__name__,
            "error_message": str(exc)
        }
    }]
    
    response = ApiResponse.error_response(
        message="服务器内部错误",
        errors=errors,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=500,
        content=response.model_dump(mode='json')
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(BaseApplicationException, application_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)