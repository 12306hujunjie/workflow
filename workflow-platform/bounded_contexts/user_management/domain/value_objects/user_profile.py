"""用户资料值对象"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """用户资料值对象"""
    
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = Field(None, max_length=500)
    timezone: str = Field(default="UTC", max_length=50)
    language: str = Field(default="zh-CN", max_length=10)
    notification_preferences: Dict[str, Any] = Field(default_factory=dict)
    
    def update(self, data: Dict[str, Any]) -> "UserProfile":
        """更新资料并返回新实例"""
        update_data = self.dict()
        update_data.update(data)
        return UserProfile(**update_data)
    
    def enable_notification(self, notification_type: str) -> "UserProfile":
        """启用某种通知"""
        new_preferences = self.notification_preferences.copy()
        new_preferences[notification_type] = True
        return self.update({"notification_preferences": new_preferences})
    
    def disable_notification(self, notification_type: str) -> "UserProfile":
        """禁用某种通知"""
        new_preferences = self.notification_preferences.copy()
        new_preferences[notification_type] = False
        return self.update({"notification_preferences": new_preferences})
    
    class Config:
        frozen = True