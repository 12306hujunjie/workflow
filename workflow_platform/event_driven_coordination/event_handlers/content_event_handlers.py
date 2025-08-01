"""内容事件处理器

处理内容模块产生的事件，协调其他模块的响应
"""

import logging
from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime

from shared_kernel.domain.events.domain_event import DomainEvent, EventHandler


logger = logging.getLogger(__name__)


class ContentPublishedEventHandler(EventHandler):
    """内容发布事件处理器
    
    当内容发布时，需要：
    1. 触发内容审核工作流
    2. 更新用户内容统计
    3. 发送发布通知
    4. 索引内容到搜索引擎
    5. 生成内容缩略图/预览
    6. 触发相关推荐更新
    """
    
    @property
    def handled_event_types(self) -> List[str]:
        """处理的事件类型列表"""
        return ["ContentPublished"]
    
    async def handle(self, event: DomainEvent) -> None:
        """处理内容发布事件"""
        try:
            content_id = event.aggregate_id
            content_data = event.event_data
            user_id = content_data.get('user_id')
            content_type = content_data.get('content_type')
            content_title = content_data.get('title')
            
            logger.info(f"Processing content publication for user {user_id}, content: {content_title}")
            
            # 1. 触发内容审核工作流
            await self._trigger_content_moderation(user_id, content_id, content_data)
            
            # 2. 更新用户内容统计
            await self._update_user_content_stats(user_id, content_data)
            
            # 3. 发送发布通知
            await self._send_publication_notification(user_id, content_data)
            
            # 4. 索引内容到搜索引擎
            await self._index_content_for_search(content_id, content_data)
            
            # 5. 生成内容缩略图/预览
            await self._generate_content_preview(content_id, content_data)
            
            # 6. 触发相关推荐更新
            await self._update_content_recommendations(user_id, content_id, content_data)
            
            logger.info(f"Successfully processed content publication for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to process content publication event: {str(e)}")
            raise
    
    async def _trigger_content_moderation(self, user_id: UUID, content_id: UUID, content_data: Dict[str, Any]) -> None:
        """触发内容审核工作流"""
        try:
            content_type = content_data.get('content_type')
            moderation_required = self._is_moderation_required(content_type, content_data)
            
            if moderation_required:
                logger.info(f"Triggering content moderation for content {content_id}")
                
                # TODO: 发布 TriggerContentModerationWorkflowEvent
                # await self.event_bus.publish(TriggerContentModerationWorkflowEvent(
                #     user_id=user_id,
                #     content_id=content_id,
                #     content_type=content_type,
                #     moderation_config=self._get_moderation_config(content_type),
                #     content_data=content_data
                # ))
            else:
                logger.info(f"Content {content_id} does not require moderation")
            
        except Exception as e:
            logger.error(f"Failed to trigger content moderation for content {content_id}: {str(e)}")
            raise
    
    async def _update_user_content_stats(self, user_id: UUID, content_data: Dict[str, Any]) -> None:
        """更新用户内容统计"""
        try:
            logger.info(f"Updating user content stats for user {user_id}")
            
            content_type = content_data.get('content_type')
            content_size = content_data.get('content_size', 0)
            
            # TODO: 发布 UpdateUserContentStatsEvent
            # await self.event_bus.publish(UpdateUserContentStatsEvent(
            #     user_id=user_id,
            #     content_type=content_type,
            #     content_size=content_size,
            #     action='publish',
            #     timestamp=datetime.utcnow()
            # ))
            
        except Exception as e:
            logger.error(f"Failed to update user content stats for user {user_id}: {str(e)}")
            # 统计更新失败不应该影响整个流程
    
    async def _send_publication_notification(self, user_id: UUID, content_data: Dict[str, Any]) -> None:
        """发送发布通知"""
        try:
            notification_settings = content_data.get('notification_settings', {})
            
            if notification_settings.get('notify_on_publish', True):
                logger.info(f"Sending publication notification for user {user_id}")
                
                # TODO: 发布 SendContentNotificationEvent
                # await self.event_bus.publish(SendContentNotificationEvent(
                #     user_id=user_id,
                #     notification_type='content_published',
                #     content_data=content_data
                # ))
            
        except Exception as e:
            logger.error(f"Failed to send publication notification for user {user_id}: {str(e)}")
            # 通知发送失败不应该影响整个流程
    
    async def _index_content_for_search(self, content_id: UUID, content_data: Dict[str, Any]) -> None:
        """索引内容到搜索引擎"""
        try:
            if content_data.get('searchable', True):
                logger.info(f"Indexing content {content_id} for search")
                
                # TODO: 发布 IndexContentForSearchEvent
                # await self.event_bus.publish(IndexContentForSearchEvent(
                #     content_id=content_id,
                #     content_data=content_data,
                #     index_config=self._get_search_index_config(content_data)
                # ))
            
        except Exception as e:
            logger.error(f"Failed to index content {content_id} for search: {str(e)}")
            # 搜索索引失败不应该影响整个流程
    
    async def _generate_content_preview(self, content_id: UUID, content_data: Dict[str, Any]) -> None:
        """生成内容缩略图/预览"""
        try:
            content_type = content_data.get('content_type')
            
            if self._requires_preview_generation(content_type):
                logger.info(f"Generating preview for content {content_id}")
                
                # TODO: 发布 GenerateContentPreviewEvent
                # await self.event_bus.publish(GenerateContentPreviewEvent(
                #     content_id=content_id,
                #     content_type=content_type,
                #     preview_config=self._get_preview_config(content_type),
                #     content_data=content_data
                # ))
            
        except Exception as e:
            logger.error(f"Failed to generate preview for content {content_id}: {str(e)}")
            # 预览生成失败不应该影响整个流程
    
    async def _update_content_recommendations(self, user_id: UUID, content_id: UUID, content_data: Dict[str, Any]) -> None:
        """更新内容推荐"""
        try:
            logger.info(f"Updating content recommendations for content {content_id}")
            
            # TODO: 发布 UpdateContentRecommendationsEvent
            # await self.event_bus.publish(UpdateContentRecommendationsEvent(
            #     user_id=user_id,
            #     content_id=content_id,
            #     content_tags=content_data.get('tags', []),
            #     content_category=content_data.get('category'),
            #     content_data=content_data
            # ))
            
        except Exception as e:
            logger.error(f"Failed to update content recommendations for content {content_id}: {str(e)}")
            # 推荐更新失败不应该影响整个流程
    
    def _is_moderation_required(self, content_type: str, content_data: Dict[str, Any]) -> bool:
        """判断是否需要内容审核"""
        # 根据内容类型和用户等级决定是否需要审核
        user_trust_level = content_data.get('user_trust_level', 'new')
        
        if user_trust_level == 'trusted':
            return False
        
        moderation_required_types = ['video', 'image', 'document']
        return content_type in moderation_required_types
    
    def _get_moderation_config(self, content_type: str) -> Dict[str, Any]:
        """获取审核配置"""
        config_mapping = {
            'video': {'check_adult_content': True, 'check_violence': True, 'check_copyright': True},
            'image': {'check_adult_content': True, 'check_violence': True, 'check_faces': True},
            'document': {'check_text_content': True, 'check_spam': True, 'check_malware': True},
            'text': {'check_spam': True, 'check_hate_speech': True}
        }
        return config_mapping.get(content_type, {})
    
    def _get_search_index_config(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取搜索索引配置"""
        return {
            'boost_factor': content_data.get('boost_factor', 1.0),
            'include_content': content_data.get('include_full_content', True),
            'language': content_data.get('language', 'en')
        }
    
    def _requires_preview_generation(self, content_type: str) -> bool:
        """判断是否需要生成预览"""
        preview_types = ['video', 'image', 'document', 'presentation']
        return content_type in preview_types
    
    def _get_preview_config(self, content_type: str) -> Dict[str, Any]:
        """获取预览生成配置"""
        config_mapping = {
            'video': {'thumbnail_count': 3, 'thumbnail_times': [0.1, 0.5, 0.9]},
            'image': {'thumbnail_sizes': ['small', 'medium', 'large']},
            'document': {'page_count': 3, 'include_text_preview': True},
            'presentation': {'slide_count': 5, 'include_notes': False}
        }
        return config_mapping.get(content_type, {})


class ContentModerationCompletedEventHandler(EventHandler):
    """内容审核完成事件处理器
    
    当内容审核完成时，需要：
    1. 更新内容状态
    2. 发送审核结果通知
    3. 如果审核通过，发布内容
    4. 如果审核不通过，通知用户修改
    5. 记录审核日志
    """
    
    @property
    def handled_event_types(self) -> List[str]:
        """处理的事件类型列表"""
        return ["ContentModerationCompleted"]
    
    async def handle(self, event: DomainEvent) -> None:
        """处理内容审核完成事件"""
        try:
            moderation_id = event.aggregate_id
            moderation_data = event.event_data
            content_id = moderation_data.get('content_id')
            user_id = moderation_data.get('user_id')
            moderation_result = moderation_data.get('result')
            
            logger.info(f"Processing content moderation completion for content {content_id}, result: {moderation_result}")
            
            # 1. 更新内容状态
            await self._update_content_status(content_id, moderation_data)
            
            # 2. 发送审核结果通知
            await self._send_moderation_result_notification(user_id, moderation_data)
            
            # 3. 根据审核结果执行相应操作
            if moderation_result == 'approved':
                await self._handle_content_approval(content_id, user_id, moderation_data)
            elif moderation_result == 'rejected':
                await self._handle_content_rejection(content_id, user_id, moderation_data)
            elif moderation_result == 'requires_review':
                await self._handle_content_manual_review(content_id, user_id, moderation_data)
            
            # 4. 记录审核日志
            await self._log_moderation_result(content_id, user_id, moderation_data)
            
            logger.info(f"Successfully processed content moderation completion for content {content_id}")
            
        except Exception as e:
            logger.error(f"Failed to process content moderation completion event: {str(e)}")
            raise
    
    async def _update_content_status(self, content_id: UUID, moderation_data: Dict[str, Any]) -> None:
        """更新内容状态"""
        try:
            moderation_result = moderation_data.get('result')
            
            status_mapping = {
                'approved': 'published',
                'rejected': 'rejected',
                'requires_review': 'pending_review'
            }
            
            new_status = status_mapping.get(moderation_result, 'unknown')
            
            logger.info(f"Updating content {content_id} status to {new_status}")
            
            # TODO: 发布 UpdateContentStatusEvent
            # await self.event_bus.publish(UpdateContentStatusEvent(
            #     content_id=content_id,
            #     new_status=new_status,
            #     moderation_data=moderation_data
            # ))
            
        except Exception as e:
            logger.error(f"Failed to update content status for content {content_id}: {str(e)}")
            raise
    
    async def _send_moderation_result_notification(self, user_id: UUID, moderation_data: Dict[str, Any]) -> None:
        """发送审核结果通知"""
        try:
            logger.info(f"Sending moderation result notification for user {user_id}")
            
            # TODO: 发布 SendContentNotificationEvent
            # await self.event_bus.publish(SendContentNotificationEvent(
            #     user_id=user_id,
            #     notification_type='moderation_completed',
            #     content_data=moderation_data
            # ))
            
        except Exception as e:
            logger.error(f"Failed to send moderation result notification for user {user_id}: {str(e)}")
            # 通知发送失败不应该影响整个流程
    
    async def _handle_content_approval(self, content_id: UUID, user_id: UUID, moderation_data: Dict[str, Any]) -> None:
        """处理内容审核通过"""
        try:
            logger.info(f"Handling content approval for content {content_id}")
            
            # TODO: 发布 ContentApprovedEvent
            # await self.event_bus.publish(ContentApprovedEvent(
            #     content_id=content_id,
            #     user_id=user_id,
            #     moderation_data=moderation_data
            # ))
            
        except Exception as e:
            logger.error(f"Failed to handle content approval for content {content_id}: {str(e)}")
            raise
    
    async def _handle_content_rejection(self, content_id: UUID, user_id: UUID, moderation_data: Dict[str, Any]) -> None:
        """处理内容审核拒绝"""
        try:
            logger.info(f"Handling content rejection for content {content_id}")
            
            rejection_reasons = moderation_data.get('rejection_reasons', [])
            
            # TODO: 发布 ContentRejectedEvent
            # await self.event_bus.publish(ContentRejectedEvent(
            #     content_id=content_id,
            #     user_id=user_id,
            #     rejection_reasons=rejection_reasons,
            #     moderation_data=moderation_data
            # ))
            
        except Exception as e:
            logger.error(f"Failed to handle content rejection for content {content_id}: {str(e)}")
            raise
    
    async def _handle_content_manual_review(self, content_id: UUID, user_id: UUID, moderation_data: Dict[str, Any]) -> None:
        """处理需要人工审核的内容"""
        try:
            logger.info(f"Handling content manual review for content {content_id}")
            
            # TODO: 发布 ContentRequiresManualReviewEvent
            # await self.event_bus.publish(ContentRequiresManualReviewEvent(
            #     content_id=content_id,
            #     user_id=user_id,
            #     review_priority=moderation_data.get('review_priority', 'normal'),
            #     moderation_data=moderation_data
            # ))
            
        except Exception as e:
            logger.error(f"Failed to handle content manual review for content {content_id}: {str(e)}")
            raise
    
    async def _log_moderation_result(self, content_id: UUID, user_id: UUID, moderation_data: Dict[str, Any]) -> None:
        """记录审核结果日志"""
        try:
            logger.info(f"Logging moderation result for content {content_id}")
            
            # TODO: 发布 ContentModerationLogEvent
            # await self.event_bus.publish(ContentModerationLogEvent(
            #     content_id=content_id,
            #     user_id=user_id,
            #     moderation_data=moderation_data,
            #     timestamp=datetime.utcnow()
            # ))
            
        except Exception as e:
            logger.error(f"Failed to log moderation result for content {content_id}: {str(e)}")
            # 日志记录失败不应该影响整个流程


class ContentDeletedEventHandler(EventHandler):
    """内容删除事件处理器
    
    当内容被删除时，需要：
    1. 清理相关文件和资源
    2. 从搜索索引中移除
    3. 更新用户内容统计
    4. 发送删除通知
    5. 清理相关推荐
    6. 记录删除日志
    """
    
    @property
    def handled_event_types(self) -> List[str]:
        """处理的事件类型列表"""
        return ["ContentDeleted"]
    
    async def handle(self, event: DomainEvent) -> None:
        """处理内容删除事件"""
        try:
            content_id = event.aggregate_id
            content_data = event.event_data
            user_id = content_data.get('user_id')
            deletion_reason = content_data.get('deletion_reason')
            
            logger.info(f"Processing content deletion for user {user_id}, reason: {deletion_reason}")
            
            # 1. 清理相关文件和资源
            await self._cleanup_content_resources(content_id, content_data)
            
            # 2. 从搜索索引中移除
            await self._remove_from_search_index(content_id, content_data)
            
            # 3. 更新用户内容统计
            await self._update_user_content_stats_for_deletion(user_id, content_data)
            
            # 4. 发送删除通知
            await self._send_deletion_notification(user_id, content_data)
            
            # 5. 清理相关推荐
            await self._cleanup_content_recommendations(content_id, content_data)
            
            # 6. 记录删除日志
            await self._log_content_deletion(content_id, user_id, content_data)
            
            logger.info(f"Successfully processed content deletion for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to process content deletion event: {str(e)}")
            raise
    
    async def _cleanup_content_resources(self, content_id: UUID, content_data: Dict[str, Any]) -> None:
        """清理内容相关资源"""
        try:
            logger.info(f"Cleaning up resources for content {content_id}")
            
            # TODO: 发布 CleanupContentResourcesEvent
            # await self.event_bus.publish(CleanupContentResourcesEvent(
            #     content_id=content_id,
            #     file_paths=content_data.get('file_paths', []),
            #     storage_locations=content_data.get('storage_locations', []),
            #     content_data=content_data
            # ))
            
        except Exception as e:
            logger.error(f"Failed to cleanup resources for content {content_id}: {str(e)}")
            raise
    
    async def _remove_from_search_index(self, content_id: UUID, content_data: Dict[str, Any]) -> None:
        """从搜索索引中移除内容"""
        try:
            logger.info(f"Removing content {content_id} from search index")
            
            # TODO: 发布 RemoveContentFromSearchEvent
            # await self.event_bus.publish(RemoveContentFromSearchEvent(
            #     content_id=content_id,
            #     content_data=content_data
            # ))
            
        except Exception as e:
            logger.error(f"Failed to remove content {content_id} from search index: {str(e)}")
            # 搜索索引移除失败不应该影响整个流程
    
    async def _update_user_content_stats_for_deletion(self, user_id: UUID, content_data: Dict[str, Any]) -> None:
        """更新用户内容统计（删除）"""
        try:
            logger.info(f"Updating user content stats for deletion, user {user_id}")
            
            content_type = content_data.get('content_type')
            content_size = content_data.get('content_size', 0)
            
            # TODO: 发布 UpdateUserContentStatsEvent
            # await self.event_bus.publish(UpdateUserContentStatsEvent(
            #     user_id=user_id,
            #     content_type=content_type,
            #     content_size=content_size,
            #     action='delete',
            #     timestamp=datetime.utcnow()
            # ))
            
        except Exception as e:
            logger.error(f"Failed to update user content stats for user {user_id}: {str(e)}")
            # 统计更新失败不应该影响整个流程
    
    async def _send_deletion_notification(self, user_id: UUID, content_data: Dict[str, Any]) -> None:
        """发送删除通知"""
        try:
            notification_settings = content_data.get('notification_settings', {})
            deletion_reason = content_data.get('deletion_reason')
            
            # 只有在非用户主动删除时才发送通知
            if deletion_reason != 'user_requested' and notification_settings.get('notify_on_delete', True):
                logger.info(f"Sending deletion notification for user {user_id}")
                
                # TODO: 发布 SendContentNotificationEvent
                # await self.event_bus.publish(SendContentNotificationEvent(
                #     user_id=user_id,
                #     notification_type='content_deleted',
                #     content_data=content_data
                # ))
            
        except Exception as e:
            logger.error(f"Failed to send deletion notification for user {user_id}: {str(e)}")
            # 通知发送失败不应该影响整个流程
    
    async def _cleanup_content_recommendations(self, content_id: UUID, content_data: Dict[str, Any]) -> None:
        """清理内容推荐"""
        try:
            logger.info(f"Cleaning up recommendations for content {content_id}")
            
            # TODO: 发布 CleanupContentRecommendationsEvent
            # await self.event_bus.publish(CleanupContentRecommendationsEvent(
            #     content_id=content_id,
            #     content_data=content_data
            # ))
            
        except Exception as e:
            logger.error(f"Failed to cleanup recommendations for content {content_id}: {str(e)}")
            # 推荐清理失败不应该影响整个流程
    
    async def _log_content_deletion(self, content_id: UUID, user_id: UUID, content_data: Dict[str, Any]) -> None:
        """记录内容删除日志"""
        try:
            logger.info(f"Logging content deletion for content {content_id}")
            
            # TODO: 发布 ContentDeletionLogEvent
            # await self.event_bus.publish(ContentDeletionLogEvent(
            #     content_id=content_id,
            #     user_id=user_id,
            #     deletion_reason=content_data.get('deletion_reason'),
            #     content_data=content_data,
            #     timestamp=datetime.utcnow()
            # ))
            
        except Exception as e:
            logger.error(f"Failed to log content deletion for content {content_id}: {str(e)}")
            # 日志记录失败不应该影响整个流程