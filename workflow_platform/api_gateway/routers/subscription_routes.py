"""订阅上下文路由聚合器"""

from fastapi import APIRouter

# TODO: 导入订阅相关的路由
# from bounded_contexts.subscription.presentation.api.subscription_routes import router as subscription_router
# from bounded_contexts.subscription.presentation.api.billing_routes import router as billing_router


def create_subscription_router() -> APIRouter:
    """创建订阅上下文的路由聚合器"""
    router = APIRouter(prefix="/subscriptions", tags=["Subscription"])
    
    # TODO: 当订阅模块实现后，添加相关路由
    # router.include_router(
    #     subscription_router,
    #     prefix="",
    #     tags=["Subscriptions"]
    # )
    # 
    # router.include_router(
    #     billing_router,
    #     prefix="/billing",
    #     tags=["Billing"]
    # )
    
    # 临时健康检查端点
    @router.get("/health")
    async def subscription_health():
        return {"status": "healthy", "context": "subscription"}
    
    return router