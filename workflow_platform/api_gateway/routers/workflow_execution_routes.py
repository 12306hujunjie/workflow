"""工作流执行上下文路由聚合器"""

from fastapi import APIRouter

# TODO: 导入工作流执行相关的路由
# from bounded_contexts.workflow_execution.presentation.api.execution_routes import router as execution_router
# from bounded_contexts.workflow_execution.presentation.api.monitoring_routes import router as monitoring_router


def create_workflow_execution_router() -> APIRouter:
    """创建工作流执行上下文的路由聚合器"""
    router = APIRouter(prefix="/executions", tags=["Workflow Execution"])
    
    # TODO: 当工作流执行模块实现后，添加相关路由
    # router.include_router(
    #     execution_router,
    #     prefix="",
    #     tags=["Executions"]
    # )
    # 
    # router.include_router(
    #     monitoring_router,
    #     prefix="/monitoring",
    #     tags=["Monitoring"]
    # )
    
    # 临时健康检查端点
    @router.get("/health")
    async def workflow_execution_health():
        return {"status": "healthy", "context": "workflow_execution"}
    
    return router