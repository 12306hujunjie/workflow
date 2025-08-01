"""Proxy performance metrics value objects."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum


class HealthStatus(Enum):
    """代理健康状态"""
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    QUARANTINED = "quarantined"


class RequestResult(Enum):
    """请求结果类型"""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_ERROR = "http_error"
    PROXY_ERROR = "proxy_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass(frozen=True)
class RequestRecord:
    """单次请求记录"""
    timestamp: datetime
    result: RequestResult
    response_time: Optional[float] = None  # milliseconds
    http_status: Optional[int] = None
    error_message: Optional[str] = None
    target_host: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        """请求是否成功"""
        return self.result == RequestResult.SUCCESS


@dataclass(frozen=True)
class ProxyMetrics:
    """代理性能指标"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0  # milliseconds
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    first_seen: Optional[datetime] = None
    last_used: Optional[datetime] = None
    request_history: List[RequestRecord] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """成功率 (0.0 - 1.0)"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def failure_rate(self) -> float:
        """失败率 (0.0 - 1.0)"""
        return 1.0 - self.success_rate
    
    @property
    def average_response_time(self) -> float:
        """平均响应时间 (milliseconds)"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests
    
    @property
    def availability_score(self) -> float:
        """可用性评分 (0.0 - 1.0)"""
        if self.total_requests == 0:
            return 0.0
        
        # 基于成功率的评分 (70% 权重)
        success_factor = self.success_rate
        
        # 基于响应时间的评分 (30% 权重)
        # 5秒以下为满分，超过5秒按比例扣分
        max_acceptable_time = 5000.0  # 5 seconds
        if self.average_response_time == 0:
            speed_factor = 1.0
        else:
            speed_factor = max(0, 1 - (self.average_response_time / max_acceptable_time))
        
        return (success_factor * 0.7) + (speed_factor * 0.3)
    
    @property
    def stability_index(self) -> float:
        """稳定性指数 (0.0 - 1.0)"""
        if self.total_requests < 10:
            return 0.5  # 请求数太少，给中等评分
        
        # 连续成功的权重
        success_streak_factor = min(1.0, self.consecutive_successes / 10.0)
        
        # 连续失败的惩罚
        failure_streak_penalty = min(1.0, self.consecutive_failures / 5.0)
        
        # 时间窗口内的稳定性（最近1小时）
        recent_stability = self._calculate_recent_stability()
        
        stability = (success_streak_factor * 0.4) + \
                   ((1 - failure_streak_penalty) * 0.3) + \
                   (recent_stability * 0.3)
        
        return max(0.0, min(1.0, stability))
    
    def _calculate_recent_stability(self) -> float:
        """计算最近1小时的稳定性"""
        if not self.request_history:
            return 0.5
        
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        recent_requests = [
            r for r in self.request_history 
            if r.timestamp >= one_hour_ago
        ]
        
        if not recent_requests:
            return 0.5
        
        recent_success_count = sum(1 for r in recent_requests if r.is_success)
        return recent_success_count / len(recent_requests)
    
    @property 
    def is_healthy(self) -> bool:
        """是否健康"""
        return (
            self.consecutive_failures < 3 and
            self.success_rate >= 0.8 and
            self.average_response_time < 10000  # 10 seconds
        )
    
    @property
    def should_quarantine(self) -> bool:
        """是否应该隔离"""
        return (
            self.consecutive_failures >= 5 or
            (self.total_requests >= 20 and self.success_rate < 0.3) or
            self.average_response_time > 30000  # 30 seconds
        )
    
    def add_request_result(
        self, 
        success: bool, 
        response_time: Optional[float] = None,
        http_status: Optional[int] = None,
        error_message: Optional[str] = None,
        target_host: Optional[str] = None
    ) -> 'ProxyMetrics':
        """添加请求结果，返回新的metrics对象"""
        now = datetime.utcnow()
        
        # 确定请求结果类型
        if success:
            result = RequestResult.SUCCESS
        elif response_time is None:
            result = RequestResult.TIMEOUT
        elif http_status and http_status >= 400:
            result = RequestResult.HTTP_ERROR
        elif "connection" in (error_message or "").lower():
            result = RequestResult.CONNECTION_ERROR
        elif "proxy" in (error_message or "").lower():
            result = RequestResult.PROXY_ERROR
        else:
            result = RequestResult.UNKNOWN_ERROR
        
        # 创建请求记录
        record = RequestRecord(
            timestamp=now,
            result=result,
            response_time=response_time,
            http_status=http_status,
            error_message=error_message,
            target_host=target_host
        )
        
        # 更新历史记录（保留最近100条）
        new_history = (self.request_history + [record])[-100:]
        
        # 计算新的指标
        new_total_requests = self.total_requests + 1
        new_successful_requests = self.successful_requests + (1 if success else 0)
        new_failed_requests = self.failed_requests + (0 if success else 1)
        new_total_response_time = self.total_response_time + (response_time or 0)
        
        # 更新连续成功/失败计数
        if success:
            new_consecutive_successes = self.consecutive_successes + 1
            new_consecutive_failures = 0
            new_last_success_time = now
            new_last_failure_time = self.last_failure_time
        else:
            new_consecutive_successes = 0
            new_consecutive_failures = self.consecutive_failures + 1
            new_last_success_time = self.last_success_time
            new_last_failure_time = now
        
        return ProxyMetrics(
            total_requests=new_total_requests,
            successful_requests=new_successful_requests,
            failed_requests=new_failed_requests,
            total_response_time=new_total_response_time,
            last_success_time=new_last_success_time,
            last_failure_time=new_last_failure_time,
            consecutive_failures=new_consecutive_failures,
            consecutive_successes=new_consecutive_successes,
            first_seen=self.first_seen or now,
            last_used=now,
            request_history=new_history
        )
    
    def get_health_status(self) -> HealthStatus:
        """获取健康状态"""
        if self.should_quarantine:
            return HealthStatus.QUARANTINED
        elif not self.is_healthy:
            return HealthStatus.UNHEALTHY
        elif self.success_rate < 0.95 or self.average_response_time > 3000:
            return HealthStatus.DEGRADED
        elif self.total_requests > 0:
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN


@dataclass(frozen=True)
class SelectionWeight:
    """代理选择权重"""
    base_weight: float = 1.0
    performance_multiplier: float = 1.0
    geo_preference_multiplier: float = 1.0
    load_balancing_multiplier: float = 1.0
    penalty_multiplier: float = 1.0
    
    @property
    def final_weight(self) -> float:
        """最终权重"""
        weight = (
            self.base_weight * 
            self.performance_multiplier * 
            self.geo_preference_multiplier * 
            self.load_balancing_multiplier * 
            self.penalty_multiplier
        )
        return max(0.0, weight)
    
    @classmethod
    def default(cls) -> 'SelectionWeight':
        """默认权重"""
        return cls()
    
    @classmethod
    def from_metrics(cls, metrics: ProxyMetrics) -> 'SelectionWeight':
        """基于指标计算权重"""
        # 性能倍数：基于可用性评分
        performance = max(0.1, metrics.availability_score)
        
        # 惩罚倍数：基于连续失败次数
        penalty = max(0.1, 1.0 - (metrics.consecutive_failures * 0.2))
        
        return cls(
            performance_multiplier=performance,
            penalty_multiplier=penalty
        )


@dataclass(frozen=True)
class HealthCheckResult:
    """健康检查结果"""
    timestamp: datetime
    success: bool
    response_time: Optional[float] = None  # milliseconds
    error_message: Optional[str] = None
    http_status: Optional[int] = None
    real_ip_detected: Optional[str] = None
    anonymity_level: Optional[int] = None  # 1=transparent, 2=anonymous, 3=elite
    target_url: Optional[str] = None
    check_type: str = "connectivity"
    
    @property
    def is_anonymous(self) -> bool:
        """是否匿名"""
        return self.anonymity_level and self.anonymity_level >= 2
    
    @property
    def is_elite(self) -> bool:
        """是否精英代理"""
        return self.anonymity_level == 3