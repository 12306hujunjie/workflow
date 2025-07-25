"""FastAPI主应用"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide

from config.settings import Settings
from container import Container, init_container
from bounded_contexts.user_management.presentation.api.user_routes import router as user_router
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
    
    # 全局异常处理
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "BAD_REQUEST",
                "message": str(exc)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        )
    
    # 注册路由
    app.include_router(user_router, prefix="/api/v1")
    
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
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )