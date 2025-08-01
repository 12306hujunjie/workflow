"""验证码服务"""

import random
import logging
from typing import Optional, Union
from datetime import timedelta
from .redis_service import RedisService

logger = logging.getLogger(__name__)


class VerificationCodeService:
    """验证码服务类"""
    
    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        self.code_length = 6
        self.expire_time = timedelta(minutes=5)  # 5分钟过期
    
    def _generate_code(self) -> str:
        """生成6位数字验证码"""
        return ''.join([str(random.randint(0, 9)) for _ in range(self.code_length)])
    
    def _get_key(self, email: str, purpose: str) -> str:
        """获取Redis键名"""
        return f"verification_code:{purpose}:{email}"
    
    async def generate_and_store_code(self, email: str, purpose: str) -> str:
        """生成并存储验证码
        
        Args:
            email: 邮箱地址
            purpose: 验证码用途 (register/reset_password)
            
        Returns:
            验证码字符串
        """
        try:
            # 生成新的验证码
            code = self._generate_code()
            key = self._get_key(email, purpose)
            
            # 存储到Redis，设置5分钟过期
            await self.redis_service.set(
                key=key,
                value=code,
                expire=self.expire_time
            )
            
            logger.info(f"验证码已生成并存储: {email}, 用途: {purpose}")
            return code
            
        except Exception as e:
            logger.error(f"生成验证码失败: {email}, 用途: {purpose}, 错误: {str(e)}")
            raise
    
    async def verify_code(self, email: str, purpose: str, code: str) -> bool:
        """验证验证码
        
        Args:
            email: 邮箱地址
            purpose: 验证码用途
            code: 用户输入的验证码
            
        Returns:
            验证是否成功
        """
        try:
            key = self._get_key(email, purpose)
            
            # 从Redis获取存储的验证码
            stored_code = await self.redis_service.get(key)
            
            if not stored_code:
                logger.warning(f"验证码不存在或已过期: {email}, 用途: {purpose}")
                return False
            
            # 验证码匹配检查
            if stored_code != code:
                logger.warning(f"验证码不匹配: {email}, 用途: {purpose}")
                return False
            
            # 验证成功，立即删除验证码（一次性使用）
            await self.redis_service.delete(key)
            logger.info(f"验证码验证成功: {email}, 用途: {purpose}")
            return True
            
        except Exception as e:
            logger.error(f"验证验证码失败: {email}, 用途: {purpose}, 错误: {str(e)}")
            return False
    
    async def is_code_exists(self, email: str, purpose: str) -> bool:
        """检查验证码是否存在（未过期）
        
        Args:
            email: 邮箱地址
            purpose: 验证码用途
            
        Returns:
            验证码是否存在
        """
        try:
            key = self._get_key(email, purpose)
            return await self.redis_service.exists(key)
        except Exception as e:
            logger.error(f"检查验证码存在性失败: {email}, 用途: {purpose}, 错误: {str(e)}")
            return False
    
    async def get_remaining_time(self, email: str, purpose: str) -> int:
        """获取验证码剩余有效时间（秒）
        
        Args:
            email: 邮箱地址
            purpose: 验证码用途
            
        Returns:
            剩余时间（秒），-1表示不存在或已过期
        """
        try:
            key = self._get_key(email, purpose)
            return await self.redis_service.ttl(key)
        except Exception as e:
            logger.error(f"获取验证码剩余时间失败: {email}, 用途: {purpose}, 错误: {str(e)}")
            return -1
    
    async def revoke_code(self, email: str, purpose: str) -> bool:
        """撤销验证码（删除）
        
        Args:
            email: 邮箱地址
            purpose: 验证码用途
            
        Returns:
            是否撤销成功
        """
        try:
            key = self._get_key(email, purpose)
            result = await self.redis_service.delete(key)
            
            if result > 0:
                logger.info(f"验证码已撤销: {email}, 用途: {purpose}")
                return True
            else:
                logger.warning(f"要撤销的验证码不存在: {email}, 用途: {purpose}")
                return False
                
        except Exception as e:
            logger.error(f"撤销验证码失败: {email}, 用途: {purpose}, 错误: {str(e)}")
            return False