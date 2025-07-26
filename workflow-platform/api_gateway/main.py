"""FastAPI主应用"""

# urllib3 1.x 版本不需要特殊的SSL警告处理

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide
from dotenv import load_dotenv

# 显式加载.env文件
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from config.settings import Settings
from container import Container, init_container
from bounded_contexts.user_management.presentation.api.user_routes import router as user_router
from bounded_contexts.user_management.presentation.api.auth_routes import router as auth_router
from bounded_contexts.user_management.presentation.api.admin_routes import router as admin_router
from shared_kernel.application.exception_handlers import register_exception_handlers
from shared_kernel.infrastructure.database.async_session import db_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("Starting up...")
    
    # 初始化依赖注入容器
    container = init_container()
    
    # 连接依赖注入
    container.wire(modules=[
        "bounded_contexts.user_management.presentation.api.user_routes",
        "bounded_contexts.user_management.presentation.api.auth_routes",
        "bounded_contexts.user_management.presentation.api.admin_routes",
        "bounded_contexts.user_management.presentation.dependencies",
        "api_gateway.middleware.auth_middleware",
        __name__
    ])
    
    yield
    
    # 关闭时
    print("Shutting down...")
    await db_config.close()


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = Settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册全局异常处理器
    register_exception_handlers(app)
    
    # 注册路由
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(user_router, prefix="/api/v1/users", tags=["User Management"])
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version
        }
    
    # 根路径
    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/api/docs"
        }
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )