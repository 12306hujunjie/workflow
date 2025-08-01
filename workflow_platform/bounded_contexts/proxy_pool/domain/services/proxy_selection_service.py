"""Proxy selection domain service - Core business logic for proxy selection."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import random
import math
from datetime import datetime

from ..entities import Proxy
from ..value_objects import (
    SelectionStrategy,
    SelectionStrategyType,
    SelectionContext,
    PerformanceThreshold
)
from ..exceptions import ProxySelectionError


class ISelectionAlgorithm(ABC):
    """选择算法接口"""
    
    @abstractmethod
    def select(
        self, 
        proxies: List[Proxy], 
        strategy: SelectionStrategy,
        context: SelectionContext
    ) -> Optional[Proxy]:
        """选择代理"""
        pass


class BestProxySelectionAlgorithm(ISelectionAlgorithm):
    """最佳代理选择算法"""
    
    def select(
        self, 
        proxies: List[Proxy], 
        strategy: SelectionStrategy,
        context: SelectionContext
    ) -> Optional[Proxy]:
        if not proxies:
            return None
        
        # 计算每个代理的评分
        scored_proxies = []
        for proxy in proxies:
            if not proxy.is_available:
                continue
            
            score = proxy.calculate_selection_score(strategy, context)
            if score > 0:
                scored_proxies.append((proxy, score))
        
        if not scored_proxies:
            return None
        
        # 选择评分最高的代理
        scored_proxies.sort(key=lambda x: x[1], reverse=True)
        return scored_proxies[0][0]


class RoundRobinSelectionAlgorithm(ISelectionAlgorithm):
    """轮询选择算法"""
    
    def __init__(self):
        self._last_selected_index = 0
    
    def select(
        self, 
        proxies: List[Proxy], 
        strategy: SelectionStrategy,
        context: SelectionContext
    ) -> Optional[Proxy]:
        if not proxies:
            return None
        
        available_proxies = [p for p in proxies if p.is_available]
        if not available_proxies:
            return None
        
        # 轮询选择
        selected_proxy = available_proxies[self._last_selected_index % len(available_proxies)]
        self._last_selected_index += 1
        
        return selected_proxy


class WeightedRandomSelectionAlgorithm(ISelectionAlgorithm):
    """权重随机选择算法"""
    
    def select(
        self, 
        proxies: List[Proxy], 
        strategy: SelectionStrategy,
        context: SelectionContext
    ) -> Optional[Proxy]:
        if not proxies:
            return None
        
        # 计算权重
        weighted_proxies = []
        total_weight = 0.0
        
        for proxy in proxies:
            if not proxy.is_available:
                continue
            
            weight = proxy.selection_weight.final_weight
            if weight > 0:
                weighted_proxies.append((proxy, weight))
                total_weight += weight
        
        if not weighted_proxies or total_weight == 0:
            return None
        
        # 权重随机选择
        random_value = random.random() * total_weight
        current_weight = 0.0
        
        for proxy, weight in weighted_proxies:
            current_weight += weight
            if random_value <= current_weight:
                return proxy
        
        # 如果没有选中（浮点数精度问题），返回最后一个
        return weighted_proxies[-1][0]


class GeoPreferredSelectionAlgorithm(ISelectionAlgorithm):
    """地域优先选择算法"""
    
    def select(
        self, 
        proxies: List[Proxy], 
        strategy: SelectionStrategy,
        context: SelectionContext
    ) -> Optional[Proxy]:
        if not proxies:
            return None
        
        available_proxies = [p for p in proxies if p.is_available]
        if not available_proxies:
            return None
        
        # 按地域偏好分组
        preferred_proxies = []
        other_proxies = []
        
        for proxy in available_proxies:
            geo_location = proxy.configuration.geo_location
            is_preferred = False
            
            # 检查上下文偏好
            if context.preferred_country and geo_location:
                if geo_location.country_code == context.preferred_country:
                    is_preferred = True
            
            # 检查策略偏好
            if strategy.geo_preference and geo_location:
                if geo_location.country_code in strategy.geo_preference.preferred_countries:
                    is_preferred = True
            
            if is_preferred:
                preferred_proxies.append(proxy)
            else:
                other_proxies.append(proxy)
        
        # 优先从偏好代理中选择
        candidates = preferred_proxies if preferred_proxies else other_proxies
        if not candidates:
            return None
        
        # 从候选代理中选择最佳的
        best_algorithm = BestProxySelectionAlgorithm()
        return best_algorithm.select(candidates, strategy, context)


class LeastUsedSelectionAlgorithm(ISelectionAlgorithm):
    """最少使用选择算法"""
    
    def select(
        self, 
        proxies: List[Proxy], 
        strategy: SelectionStrategy,
        context: SelectionContext
    ) -> Optional[Proxy]:
        if not proxies:
            return None
        
        available_proxies = [p for p in proxies if p.is_available]
        if not available_proxies:
            return None
        
        # 选择并发请求数最少的代理
        least_used_proxy = min(
            available_proxies,
            key=lambda p: p.current_concurrent_requests
        )
        
        return least_used_proxy


class FastestSelectionAlgorithm(ISelectionAlgorithm):
    """最快响应选择算法"""
    
    def select(
        self, 
        proxies: List[Proxy], 
        strategy: SelectionStrategy,
        context: SelectionContext
    ) -> Optional[Proxy]:
        if not proxies:
            return None
        
        # 过滤可用代理并且有响应时间记录的
        fast_proxies = []
        for proxy in proxies:
            if (proxy.is_available and 
                proxy.metrics.average_response_time > 0 and
                proxy.metrics.total_requests >= 5):  # 至少有5次请求记录
                fast_proxies.append(proxy)
        
        if not fast_proxies:
            # 如果没有足够的历史数据，回退到最佳选择
            return BestProxySelectionAlgorithm().select(proxies, strategy, context)
        
        # 选择响应时间最快的
        fastest_proxy = min(
            fast_proxies,
            key=lambda p: p.metrics.average_response_time
        )
        
        return fastest_proxy


class MostReliableSelectionAlgorithm(ISelectionAlgorithm):
    """最可靠选择算法"""
    
    def select(
        self, 
        proxies: List[Proxy], 
        strategy: SelectionStrategy,
        context: SelectionContext
    ) -> Optional[Proxy]:
        if not proxies:
            return None
        
        # 过滤可用且有足够历史记录的代理
        reliable_proxies = []
        for proxy in proxies:
            if (proxy.is_available and 
                proxy.metrics.total_requests >= 10):  # 至少10次请求记录
                reliable_proxies.append(proxy)
        
        if not reliable_proxies:
            # 如果没有足够的历史数据，回退到最佳选择
            return BestProxySelectionAlgorithm().select(proxies, strategy, context)
        
        # 按成功率和稳定性选择
        most_reliable = max(
            reliable_proxies,
            key=lambda p: (p.metrics.success_rate * 0.7 + p.metrics.stability_index * 0.3)
        )
        
        return most_reliable


class ProxySelectionService:
    """代理选择领域服务"""
    
    def __init__(self):
        self._algorithms: Dict[SelectionStrategyType, ISelectionAlgorithm] = {
            SelectionStrategyType.BEST: BestProxySelectionAlgorithm(),
            SelectionStrategyType.ROUND_ROBIN: RoundRobinSelectionAlgorithm(),
            SelectionStrategyType.WEIGHTED: WeightedRandomSelectionAlgorithm(),
            SelectionStrategyType.GEO_PREFERRED: GeoPreferredSelectionAlgorithm(),
            SelectionStrategyType.LEAST_USED: LeastUsedSelectionAlgorithm(),
            SelectionStrategyType.FASTEST: FastestSelectionAlgorithm(),
            SelectionStrategyType.MOST_RELIABLE: MostReliableSelectionAlgorithm(),
            SelectionStrategyType.RANDOM: WeightedRandomSelectionAlgorithm(),  # 使用权重随机
        }
    
    def select_optimal_proxy(
        self, 
        available_proxies: List[Proxy], 
        strategy: SelectionStrategy,
        context: SelectionContext
    ) -> Optional[Proxy]:
        """选择最优代理"""
        if not available_proxies:
            return None
        
        # 应用性能阈值过滤
        filtered_proxies = self._apply_performance_threshold(
            available_proxies, strategy.performance_threshold
        )
        
        if not filtered_proxies:
            # 如果严格过滤后没有代理，尝试宽松过滤
            filtered_proxies = self._apply_loose_performance_threshold(
                available_proxies, strategy.performance_threshold
            )
        
        if not filtered_proxies:
            return None
        
        try:
            # 使用选择算法
            algorithm = self._algorithms.get(strategy.strategy_type)
            if not algorithm:
                raise ProxySelectionError(f"Unknown selection strategy: {strategy.strategy_type}")
            
            selected_proxy = algorithm.select(filtered_proxies, strategy, context)
            
            # 如果主策略失败，尝试回退策略
            if not selected_proxy and strategy.fallback_strategy:
                fallback_algorithm = self._algorithms.get(strategy.fallback_strategy)
                if fallback_algorithm:
                    selected_proxy = fallback_algorithm.select(filtered_proxies, strategy, context)
            
            return selected_proxy
            
        except Exception as e:
            raise ProxySelectionError(f"Selection algorithm failed: {str(e)}") from e
    
    def _apply_performance_threshold(
        self, 
        proxies: List[Proxy], 
        threshold: PerformanceThreshold
    ) -> List[Proxy]:
        """应用性能阈值过滤"""
        filtered = []
        
        for proxy in proxies:
            if not proxy.is_available:
                continue
            
            metrics = proxy.metrics
            
            # 成功率检查
            if metrics.success_rate < threshold.min_success_rate:
                continue
            
            # 响应时间检查
            if (metrics.average_response_time > 0 and 
                metrics.average_response_time > threshold.max_response_time):
                continue
            
            # 可用性评分检查
            if metrics.availability_score < threshold.min_availability_score:
                continue
            
            # 连续失败检查
            if metrics.consecutive_failures > threshold.max_consecutive_failures:
                continue
            
            filtered.append(proxy)
        
        return filtered
    
    def _apply_loose_performance_threshold(
        self, 
        proxies: List[Proxy], 
        threshold: PerformanceThreshold
    ) -> List[Proxy]:
        """应用宽松的性能阈值过滤"""
        filtered = []
        
        for proxy in proxies:
            if not proxy.is_available:
                continue
            
            metrics = proxy.metrics
            
            # 宽松的成功率检查（降低50%）
            if metrics.success_rate < (threshold.min_success_rate * 0.5):
                continue
            
            # 宽松的响应时间检查（增加50%）
            if (metrics.average_response_time > 0 and 
                metrics.average_response_time > (threshold.max_response_time * 1.5)):
                continue
            
            # 连续失败检查（增加50%）
            if metrics.consecutive_failures > (threshold.max_consecutive_failures * 1.5):
                continue
            
            filtered.append(proxy)
        
        return filtered
    
    def calculate_pool_health_score(self, proxies: List[Proxy]) -> float:
        """计算代理池健康评分"""
        if not proxies:
            return 0.0
        
        total_score = 0.0
        active_count = 0
        
        for proxy in proxies:
            if proxy.is_available:
                total_score += proxy.metrics.availability_score
                active_count += 1
        
        if active_count == 0:
            return 0.0
        
        # 平均可用性评分 * 可用代理比例
        avg_availability = total_score / active_count
        availability_ratio = active_count / len(proxies)
        
        return avg_availability * availability_ratio
    
    def get_selection_statistics(self, proxies: List[Proxy]) -> Dict[str, any]:
        """获取选择统计信息"""
        if not proxies:
            return {
                'total_proxies': 0,
                'available_proxies': 0,
                'average_response_time': 0.0,
                'average_success_rate': 0.0,
                'pool_health_score': 0.0
            }
        
        available_proxies = [p for p in proxies if p.is_available]
        
        if available_proxies:
            avg_response_time = sum(
                p.metrics.average_response_time for p in available_proxies 
                if p.metrics.average_response_time > 0
            ) / len([p for p in available_proxies if p.metrics.average_response_time > 0])
            
            avg_success_rate = sum(p.metrics.success_rate for p in available_proxies) / len(available_proxies)
        else:
            avg_response_time = 0.0
            avg_success_rate = 0.0
        
        return {
            'total_proxies': len(proxies),
            'available_proxies': len(available_proxies),
            'average_response_time': avg_response_time,
            'average_success_rate': avg_success_rate,
            'pool_health_score': self.calculate_pool_health_score(proxies)
        }