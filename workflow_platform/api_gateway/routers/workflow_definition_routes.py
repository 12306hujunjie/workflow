"""工作流定义上下文路由聚合器"""

from fastapi import APIRouter

# TODO: 导入工作流定义相关的路由
# from bounded_contexts.workflow_definition.presentation.api.definition_routes import router as definition_router
# from bounded_contexts.workflow_definition.presentation.api.template_routes import router as template_router


def create_workflow_definition_router() -> APIRouter:
    """创建工作流定义上下文的路由聚合器"""
    router = APIRouter(prefix="/definitions", tags=["Workflow Definition"])
    
    # TODO: 当工作流定义模块实现后，添加相关路由
    # router.include_router(
    #     definition_router,
    #     prefix="",
    #     tags=["Definitions"]
    # )
    # 
    # router.include_router(
    #     template_router,
    #     prefix="/templates",
    #     tags=["Templates"]
    # )
    
    # 临时健康检查端点
    @router.get("/health")
    async def workflow_definition_health():
        return {"status": "healthy", "context": "workflow_definition"}
    
    return router