"""认证中间件"""

from typing import Optional
from fastapi import HTTPException, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dependency_injector.wiring import Provide, inject

from bounded_contexts.user_management.infrastructure.auth.jwt_service import JWTService
from container import Container


class JWTBearer(HTTPBearer):
    """JWT Bearer认证"""
    
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[dict]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )
            payload = await self.verify_jwt(credentials.credentials)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token."
                )
            return payload
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )
    
    @inject
    async def verify_jwt(
        self, 
        token: str,
        jwt_service: JWTService = Provide[Container.jwt_service]
    ) -> Optional[dict]:
        """验证JWT令牌"""
        try:
            payload = await jwt_service.verify_access_token(token)
            return payload
        except Exception as e:
            print(f"JWT verification error: {e}")
            return None


jwt_bearer = JWTBearer()


async def get_current_user_id(
    credentials: dict = Depends(jwt_bearer),
) -> int:
    """获取当前用户ID"""
    return credentials["user_id"]


async def get_current_user_role(
    credentials: dict = Depends(jwt_bearer),
) -> str:
    """获取当前用户角色"""
    return credentials["role"]


async def require_admin(role: str = Depends(get_current_user_role)) -> str:
    """需要管理员权限"""
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required."
        )
    return role