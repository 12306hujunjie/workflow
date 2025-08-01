"""主路由聚合器"""

from fastapi import APIRouter

from .user_management_routes import create_user_management_router
from .workflow_execution_routes import create_workflow_execution_router
from .workflow_definition_routes import create_workflow_definition_router
from .subscription_routes import create_subscription_router


def create_api_router(api_prefix: str = "/api/v1") -> APIRouter:
    """创建主API路由聚合器
    
    Args:
        api_prefix: API前缀，默认为/api/v1
        
    Returns:
        配置好的主路由器
    """
    router = APIRouter(prefix=api_prefix)
    
    # 用户管理上下文
    router.include_router(
        create_user_management_router(),
        tags=["User Management"]
    )
    
    # 工作流执行上下文
    router.include_router(
        create_workflow_execution_router(),
        tags=["Workflow Execution"]
    )
    
    # 工作流定义上下文
    router.include_router(
        create_workflow_definition_router(),
        tags=["Workflow Definition"]
    )
    
    # 订阅上下文
    router.include_router(
        create_subscription_router(),
        tags=["Subscription"]
    )
    
    # API健康检查
    @router.get("/health")
    async def api_health():
        return {
            "status": "healthy",
            "api_version": "v1",
            "contexts": [
                "user_management",
                "workflow_execution", 
                "workflow_definition",
                "subscription"
            ]
        }
    
    return router