"""用户登录历史服务"""

from typing import List, Dict, Any
from datetime import datetime, timezone
from ...domain.repositories.user_repository import UserRepository
from ...infrastructure.models.user_models import UserLoginHistoryModel


class UserLoginHistoryService:
    """用户登录历史服务"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    async def get_user_login_history(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """获取用户登录历史"""
        try:
            # 从数据库获取登录历史
            history_records = await self._user_repository.get_login_history(
                user_id=user_id,
                page=page,
                limit=limit
            )
            
            # 转换为响应格式
            items = []
            for record in history_records.get('items', []):
                items.append({
                    "id": record.id,
                    "ip_address": record.ip_address,
                    "user_agent": record.user_agent,
                    "login_at": record.created_at.isoformat() if record.created_at else None,
                    "location": record.location_info.get('city', '未知位置') if record.location_info else "未知位置",
                    "success": record.login_status == "success"
                })
            
            return {
                "items": items,
                "total": history_records.get('total', 0),
                "page": page,
                "limit": limit,
                "total_pages": (history_records.get('total', 0) + limit - 1) // limit
            }
            
        except Exception as e:
            # 如果数据库查询失败，返回空结果而不是崩溃
            return {
                "items": [],
                "total": 0,
                "page": page,
                "limit": limit, 
                "total_pages": 0
            }
    
    async def record_login(
        self,
        user_id: int,
        ip_address: str,
        user_agent: str,
        success: bool = True,
        location: str = None
    ) -> None:
        """记录用户登录"""
        try:
            login_record = {
                "user_id": user_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "login_at": datetime.now(timezone.utc),
                "success": success,
                "location": location or "未知位置"
            }
            
            await self._user_repository.save_login_history(login_record)
            
        except Exception as e:
            # 登录历史记录失败不应该影响登录流程，只记录错误
            print(f"Failed to record login history: {str(e)}")
            pass