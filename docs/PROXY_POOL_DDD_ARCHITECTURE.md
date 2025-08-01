# 代理池系统DDD架构设计 (Proxy Pool System - DDD Architecture)

## 📋 项目概述 (Project Overview)

基于DDD (Domain-Driven Design) 架构风格，为当前工作流平台设计和实现一个高可用、智能化的代理池系统。该系统将通过依赖注入容器集成到现有平台中，为各个bounded context提供可靠的代理服务。

## 🏗️ DDD架构设计 (DDD Architecture Design)

### 1. Domain Layer (领域层)

#### 1.1 核心实体 (Core Entities)

```python
# domain/entities/proxy.py
class Proxy(BaseEntity):
    """代理聚合根 - 管理代理的完整生命周期"""
    
    def __init__(self, proxy_id: ProxyId, configuration: ProxyConfiguration):
        super().__init__(proxy_id)
        self._configuration = configuration
        self._metrics = ProxyMetrics()
        self._health_status = HealthStatus.UNKNOWN
        self._selection_weight = SelectionWeight.default()
        self._domain_events: List[DomainEvent] = []
    
    # 核心业务逻辑
    def test_connectivity(self, health_checker: IProxyHealthChecker) -> HealthCheckResult
    def update_metrics(self, request_result: RequestResult) -> None
    def calculate_selection_score(self, strategy: SelectionStrategy) -> float
    def mark_as_failed(self, failure_reason: str) -> None
    def recover_from_failure(self) -> None
```

#### 1.2 值对象 (Value Objects)

```python
# domain/value_objects/proxy_metrics.py
@dataclass(frozen=True)
class ProxyMetrics:
    """代理性能指标"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def availability_score(self) -> float:
        """基于成功率和响应时间的可用性评分"""
        success_factor = self.success_rate
        speed_factor = max(0, 1 - (self.average_response_time / 5000))  # 5秒为基准
        return (success_factor * 0.7) + (speed_factor * 0.3)

# domain/value_objects/selection_strategy.py
@dataclass(frozen=True)  
class SelectionStrategy:
    """代理选择策略"""
    strategy_type: SelectionStrategyType
    geo_preferences: List[str] = field(default_factory=list)
    performance_threshold: float = 0.8
    max_concurrent_per_proxy: int = 10
    
    def calculate_score(self, proxy: Proxy, context: SelectionContext) -> float:
        """根据策略计算代理评分"""
        pass
```

#### 1.3 领域服务 (Domain Services)

```python
# domain/services/proxy_selection_service.py
class ProxySelectionService:
    """代理选择领域服务"""
    
    def __init__(self, strategies: Dict[SelectionStrategyType, ISelectionAlgorithm]):
        self._strategies = strategies
    
    def select_optimal_proxy(
        self, 
        available_proxies: List[Proxy], 
        strategy: SelectionStrategy,
        context: SelectionContext
    ) -> Optional[Proxy]:
        """选择最优代理"""
        algorithm = self._strategies[strategy.strategy_type]
        return algorithm.select(available_proxies, strategy, context)

# domain/services/proxy_health_service.py  
class ProxyHealthService:
    """代理健康管理领域服务"""
    
    async def perform_health_check(
        self, 
        proxy: Proxy, 
        config: HealthCheckConfig
    ) -> HealthCheckResult:
        """执行健康检查"""
        pass
    
    def should_quarantine_proxy(self, proxy: Proxy) -> bool:
        """判断是否应该隔离代理"""
        return proxy.metrics.consecutive_failures >= 3
```

### 2. Application Layer (应用层)

#### 2.1 应用服务 (Application Services)

```python
# application/services/proxy_pool_application_service.py
class ProxyPoolApplicationService:
    """代理池应用服务 - 协调各种用例"""
    
    def __init__(
        self,
        proxy_repository: IProxyRepository,
        health_service: ProxyHealthService,
        selection_service: ProxySelectionService,
        event_publisher: IEventPublisher
    ):
        self._proxy_repository = proxy_repository
        self._health_service = health_service
        self._selection_service = selection_service
        self._event_publisher = event_publisher
    
    async def get_available_proxy(
        self, 
        request: GetProxyRequest
    ) -> GetProxyResponse:
        """获取可用代理 - 核心用例"""
        try:
            # 1. 获取可用代理列表
            available_proxies = await self._proxy_repository.find_available_proxies(
                filters=request.filters
            )
            
            if not available_proxies:
                raise NoAvailableProxyError("No proxies available")
            
            # 2. 应用选择策略
            selected_proxy = self._selection_service.select_optimal_proxy(
                available_proxies, 
                request.selection_strategy,
                request.context
            )
            
            if not selected_proxy:
                raise ProxySelectionError("Failed to select proxy")
            
            # 3. 更新使用记录
            selected_proxy.record_usage()
            await self._proxy_repository.save(selected_proxy)
            
            # 4. 发布领域事件
            event = ProxySelectedEvent(
                proxy_id=selected_proxy.id,
                strategy=request.selection_strategy,
                timestamp=datetime.utcnow()
            )
            await self._event_publisher.publish(event)
            
            return GetProxyResponse(proxy=selected_proxy)
            
        except Exception as e:
            # 统一异常处理
            raise ProxyPoolApplicationError(f"Failed to get proxy: {str(e)}") from e
```

#### 2.2 用例 (Use Cases)

```python
# application/use_cases/manage_proxy_health.py
class ManageProxyHealthUseCase:
    """管理代理健康状态用例"""
    
    async def execute(self, command: HealthCheckCommand) -> HealthCheckResult:
        """执行健康检查"""
        proxy = await self._proxy_repository.find_by_id(command.proxy_id)
        if not proxy:
            raise ProxyNotFoundError(f"Proxy {command.proxy_id} not found")
        
        # 执行健康检查
        result = await self._health_service.perform_health_check(
            proxy, command.config
        )
        
        # 更新代理状态
        proxy.update_health_status(result)
        await self._proxy_repository.save(proxy)
        
        return result

# application/use_cases/report_proxy_result.py
class ReportProxyResultUseCase:
    """报告代理使用结果用例"""
    
    async def execute(self, command: ReportResultCommand) -> None:
        """报告使用结果"""
        proxy = await self._proxy_repository.find_by_id(command.proxy_id)
        if not proxy:
            return  # 忽略不存在的代理
        
        # 更新指标
        result = RequestResult(
            success=command.success,
            response_time=command.response_time,
            error_code=command.error_code,
            timestamp=datetime.utcnow()
        )
        
        proxy.update_metrics(result)
        
        # 检查是否需要标记为失败
        if self._health_service.should_quarantine_proxy(proxy):
            proxy.mark_as_failed("Consecutive failures threshold exceeded")
        
        await self._proxy_repository.save(proxy)
```

### 3. Infrastructure Layer (基础设施层)

#### 3.1 仓储实现 (Repository Implementation)

```python
# infrastructure/repositories/sqlalchemy_proxy_repository.py
class SQLAlchemyProxyRepository(IProxyRepository):
    """SQLAlchemy代理仓储实现"""
    
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self._session_factory = session_factory
    
    async def save(self, proxy: Proxy) -> None:
        """保存代理"""
        async with self._session_factory() as session:
            model = await session.get(ProxyModel, proxy.id.value)
            
            if model is None:
                model = ProxyModel()
                session.add(model)
            
            # 映射领域对象到数据模型
            self._map_to_model(proxy, model)
            
            await session.commit()
    
    async def find_available_proxies(
        self, 
        filters: ProxyFilters,
        limit: int = 50
    ) -> List[Proxy]:
        """查找可用代理"""
        async with self._session_factory() as session:
            query = select(ProxyModel).where(
                ProxyModel.status == ProxyStatus.ACTIVE.value
            )
            
            # 应用过滤器
            if filters.country_codes:
                query = query.where(ProxyModel.country_code.in_(filters.country_codes))
            
            if filters.protocols:
                query = query.where(ProxyModel.protocol.in_([p.value for p in filters.protocols]))
            
            # 性能排序
            query = query.order_by(
                desc(ProxyModel.success_rate),
                asc(ProxyModel.average_response_time)
            ).limit(limit)
            
            result = await session.execute(query)
            models = result.scalars().all()
            
            return [self._map_to_domain(model) for model in models]
```

#### 3.2 健康检查器实现 (Health Checker Implementation)

```python
# infrastructure/health/async_proxy_health_checker.py
class AsyncProxyHealthChecker(IProxyHealthChecker):
    """异步代理健康检查器"""
    
    def __init__(self, http_client: aiohttp.ClientSession):
        self._http_client = http_client
    
    async def check_connectivity(
        self, 
        proxy: Proxy, 
        config: HealthCheckConfig
    ) -> HealthCheckResult:
        """检查连接性"""
        try:
            start_time = time.time()
            
            async with self._http_client.get(
                config.test_url,
                proxy=proxy.configuration.url,
                timeout=aiohttp.ClientTimeout(total=config.timeout)
            ) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                if response.status == 200:
                    # 检查IP匿名性
                    response_data = await response.json()
                    anonymity_result = await self._check_anonymity(
                        response_data, proxy, config
                    )
                    
                    return HealthCheckResult(
                        success=True,
                        response_time=response_time,
                        anonymity_level=anonymity_result.level,
                        real_ip_detected=anonymity_result.real_ip_detected
                    )
                else:
                    return HealthCheckResult(
                        success=False,
                        error_message=f"HTTP {response.status}"
                    )
                    
        except Exception as e:
            return HealthCheckResult(
                success=False,
                error_message=str(e)
            )
```

### 4. Presentation Layer (表示层)

由于是内部使用，表示层主要是提供给其他bounded context的接口：

```python
# presentation/interfaces/proxy_pool_facade.py
class ProxyPoolFacade:
    """代理池门面 - 对外统一接口"""
    
    def __init__(self, application_service: ProxyPoolApplicationService):
        self._application_service = application_service
    
    async def get_proxy(
        self,
        country_code: Optional[str] = None,
        protocol: Optional[ProxyProtocol] = None,
        strategy: SelectionStrategyType = SelectionStrategyType.BEST
    ) -> Optional[ProxyInfo]:
        """获取代理 - 简化接口"""
        request = GetProxyRequest(
            filters=ProxyFilters(
                country_codes=[country_code] if country_code else [],
                protocols=[protocol] if protocol else []
            ),
            selection_strategy=SelectionStrategy(strategy_type=strategy)
        )
        
        try:
            response = await self._application_service.get_available_proxy(request)
            return self._to_proxy_info(response.proxy)
        except NoAvailableProxyError:
            return None
        except Exception as e:
            # 记录日志但不抛出异常，保证其他服务的健壮性
            logger.error(f"Failed to get proxy: {e}")
            return None
    
    async def report_result(
        self, 
        proxy_id: str, 
        success: bool, 
        response_time: Optional[float] = None
    ) -> None:
        """报告使用结果"""
        command = ReportResultCommand(
            proxy_id=ProxyId(proxy_id),
            success=success,
            response_time=response_time
        )
        
        try:
            await self._application_service.report_proxy_result(command)
        except Exception as e:
            logger.error(f"Failed to report proxy result: {e}")
            # 不抛出异常，避免影响业务流程
```

## 🔧 依赖注入容器集成 (DI Container Integration)

### 1. 容器配置扩展

```python
# container.py 中添加代理池相关服务
class Container(containers.DeclarativeContainer):
    # ... 现有配置 ...
    
    # 代理池基础设施
    proxy_health_checker = providers.Singleton(
        AsyncProxyHealthChecker,
        http_client=providers.Singleton(aiohttp.ClientSession)
    )
    
    # 代理池仓储
    proxy_repository = providers.Factory(
        SQLAlchemyProxyRepository,
        session_factory=database_config.provided.get_session
    )
    
    # 代理池领域服务
    proxy_selection_service = providers.Singleton(
        ProxySelectionService,
        strategies=providers.Dict({
            SelectionStrategyType.BEST: providers.Factory(BestProxySelectionAlgorithm),
            SelectionStrategyType.ROUND_ROBIN: providers.Factory(RoundRobinSelectionAlgorithm),
            SelectionStrategyType.WEIGHTED: providers.Factory(WeightedSelectionAlgorithm),
            SelectionStrategyType.GEO_PREFERRED: providers.Factory(GeoPreferredSelectionAlgorithm)
        })
    )
    
    proxy_health_service = providers.Singleton(
        ProxyHealthService,
        health_checker=proxy_health_checker,
        quarantine_threshold=config.provided.proxy_quarantine_threshold
    )
    
    # 代理池应用服务
    proxy_pool_application_service = providers.Factory(
        ProxyPoolApplicationService,
        proxy_repository=proxy_repository,
        health_service=proxy_health_service,
        selection_service=proxy_selection_service,
        event_publisher=providers.Singleton(DomainEventPublisher)
    )
    
    # 代理池门面 - 对外接口
    proxy_pool_facade = providers.Singleton(
        ProxyPoolFacade,
        application_service=proxy_pool_application_service
    )
```

### 2. 其他Bounded Context集成示例

```python
# bounded_contexts/qidian/application/services/content_crawler_service.py
class ContentCrawlerService:
    """起点内容爬虫服务"""
    
    def __init__(
        self,
        proxy_pool: ProxyPoolFacade,  # 注入代理池
        http_client: aiohttp.ClientSession
    ):
        self._proxy_pool = proxy_pool
        self._http_client = http_client
    
    async def crawl_novel_info(self, novel_id: str) -> NovelInfo:
        """爬取小说信息"""
        # 获取代理
        proxy = await self._proxy_pool.get_proxy(
            country_code="CN",  # 中国代理
            protocol=ProxyProtocol.HTTPS,
            strategy=SelectionStrategyType.BEST
        )
        
        url = f"https://book.qidian.com/info/{novel_id}"
        
        try:
            # 使用代理发送请求
            async with self._http_client.get(
                url, 
                proxy=proxy.url if proxy else None
            ) as response:
                if response.status == 200:
                    # 成功 - 报告结果
                    if proxy:
                        await self._proxy_pool.report_result(
                            proxy.id, 
                            success=True, 
                            response_time=response.headers.get('X-Response-Time')
                        )
                    
                    return await self._parse_novel_info(response)
                else:
                    raise CrawlError(f"HTTP {response.status}")
                    
        except Exception as e:
            # 失败 - 报告结果
            if proxy:
                await self._proxy_pool.report_result(proxy.id, success=False)
            raise
```

## 📊 监控和可观测性 (Monitoring & Observability)

### 1. 领域事件 (Domain Events)

```python
# domain/events/proxy_events.py
@dataclass(frozen=True)
class ProxySelectedEvent(DomainEvent):
    """代理被选中事件"""
    proxy_id: ProxyId
    strategy: SelectionStrategy
    context: SelectionContext
    timestamp: datetime

@dataclass(frozen=True)
class ProxyHealthChangedEvent(DomainEvent):
    """代理健康状态改变事件"""
    proxy_id: ProxyId
    old_status: HealthStatus
    new_status: HealthStatus
    check_result: HealthCheckResult
    timestamp: datetime

@dataclass(frozen=True)
class ProxyQuarantinedEvent(DomainEvent):
    """代理被隔离事件"""
    proxy_id: ProxyId
    reason: str
    consecutive_failures: int
    timestamp: datetime
```

### 2. 事件处理器 (Event Handlers)

```python
# infrastructure/event_handlers/proxy_monitoring_handler.py
class ProxyMonitoringEventHandler:
    """代理监控事件处理器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self._metrics = metrics_collector
    
    async def handle_proxy_selected(self, event: ProxySelectedEvent) -> None:
        """处理代理选择事件"""
        # 记录选择指标
        self._metrics.increment_counter(
            "proxy_selections_total",
            labels={
                "proxy_id": event.proxy_id.value,
                "strategy": event.strategy.strategy_type.value,
                "country": event.context.preferred_country or "any"
            }
        )
    
    async def handle_proxy_quarantined(self, event: ProxyQuarantinedEvent) -> None:
        """处理代理隔离事件"""
        # 发送告警
        await self._send_alert(
            f"Proxy {event.proxy_id.value} quarantined: {event.reason}"
        )
        
        # 记录隔离指标
        self._metrics.increment_counter(
            "proxy_quarantines_total",
            labels={"reason": event.reason}
        )
```

## 🧪 测试策略 (Testing Strategy)

### 1. 单元测试 (Unit Tests)

```python
# tests/unit/domain/entities/test_proxy.py
class TestProxy:
    """代理实体单元测试"""
    
    def test_calculate_selection_score_with_high_performance(self):
        """测试高性能代理的选择评分"""
        # Arrange
        proxy = self._create_high_performance_proxy()
        strategy = SelectionStrategy(SelectionStrategyType.BEST)
        context = SelectionContext()
        
        # Act
        score = proxy.calculate_selection_score(strategy)
        
        # Assert
        assert score > 0.8
    
    def test_mark_as_failed_publishes_domain_event(self):
        """测试标记失败时发布领域事件"""
        # Arrange
        proxy = self._create_active_proxy()
        
        # Act
        proxy.mark_as_failed("Connection timeout")
        
        # Assert
        events = proxy.domain_events
        assert len(events) == 1
        assert isinstance(events[0], ProxyHealthChangedEvent)
```

### 2. 集成测试 (Integration Tests)

```python
# tests/integration/test_proxy_pool_integration.py
class TestProxyPoolIntegration:
    """代理池集成测试"""
    
    async def test_get_proxy_end_to_end(self, container):
        """端到端代理获取测试"""
        # Arrange
        facade = container.proxy_pool_facade()
        await self._seed_test_proxies()
        
        # Act
        proxy = await facade.get_proxy(country_code="US")
        
        # Assert
        assert proxy is not None
        assert proxy.geo_location.country_code == "US"
        assert proxy.status == ProxyStatus.ACTIVE
```

## 🚀 实施路线图 (Implementation Roadmap)

### Phase 1: 核心领域模型 (2周)
- [x] 完善值对象定义
- [ ] 实现Proxy聚合根
- [ ] 实现领域服务
- [ ] 基础仓储接口

### Phase 2: 应用层和基础设施 (3周)  
- [ ] 应用服务实现
- [ ] SQLAlchemy仓储实现
- [ ] 健康检查器实现
- [ ] 依赖注入集成

### Phase 3: 高级功能 (2周)
- [ ] 多种选择策略
- [ ] 事件驱动监控
- [ ] 性能优化
- [ ] 完整测试覆盖

### Phase 4: 生产就绪 (1周)
- [ ] 监控告警
- [ ] 文档完善  
- [ ] 性能基准测试
- [ ] 部署脚本

## 📈 预期收益 (Expected Benefits)

### 业务价值
- **提高爬虫成功率**: 从当前的70%提升到95%+
- **降低IP封禁风险**: 智能轮换和健康检查
- **统一代理管理**: 各bounded context共享代理资源

### 技术价值  
- **清晰的架构边界**: DDD确保代码组织清晰
- **高可测试性**: 依赖注入使测试更容易
- **事件驱动监控**: 实时了解系统健康状态
- **水平扩展能力**: 支持大规模代理池管理

---

*此架构设计将随着开发进展持续演进和完善。*