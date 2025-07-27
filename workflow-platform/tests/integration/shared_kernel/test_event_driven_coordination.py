"""事件驱动协调模块测试

测试事件驱动架构的核心功能，包括事件存储、发布、处理等
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from shared_kernel.domain.events.domain_event import DomainEvent, EventHandler
from shared_kernel.domain.events.event_store import InMemoryEventStore
from shared_kernel.infrastructure.event_publisher import InMemoryEventPublisher
from event_driven_coordination.event_bus import EventBus, EventBusFactory
from event_driven_coordination import (
    EventDrivenCoordinator,
    get_coordinator,
    shutdown_coordinator,
    publish_event,
    publish_events,
    register_handler
)


class TestDomainEvent(DomainEvent):
    """测试用领域事件"""
    
    def __init__(self, aggregate_id, event_type, event_data, occurred_at=None):
        # 创建包含event_type的event_data
        enhanced_event_data = dict(event_data) if event_data else {}
        enhanced_event_data['event_type'] = event_type
        
        super().__init__(aggregate_id, enhanced_event_data)
        self._event_type = event_type
        if occurred_at:
            self.occurred_at = occurred_at
    
    @property
    def event_type(self) -> str:
        return self._event_type
    
    @property
    def aggregate_type(self) -> str:
        return "TestAggregate"


class TestEventHandler(EventHandler):
    """测试用事件处理器"""
    
    def __init__(self, event_types=None):
        self.handled_events = []
        self.handle_count = 0
        self.should_fail = False
        self._handled_event_types = event_types or ["TestEvent"]
    
    @property
    def handled_event_types(self) -> List[str]:
        """处理的事件类型列表"""
        return self._handled_event_types
    
    async def handle(self, event):
        self.handle_count += 1
        if self.should_fail:
            raise Exception(f"Handler failed for event {event.event_type}")
        self.handled_events.append(event)


@pytest.fixture
async def event_bus():
    """创建测试用事件总线"""
    event_store = InMemoryEventStore()
    event_publisher = InMemoryEventPublisher()
    bus = EventBus(event_store, event_publisher)
    return bus


@pytest.fixture
async def coordinator(event_bus):
    """创建测试用协调器"""
    coordinator = EventDrivenCoordinator(
        event_store=event_bus.event_store,
        event_publisher=event_bus.event_publisher,
        event_bus=event_bus
    )
    await coordinator.initialize()
    yield coordinator
    await coordinator.shutdown()


@pytest.fixture
def sample_event():
    """创建示例事件"""
    return TestDomainEvent(
        aggregate_id=uuid4(),
        event_type="TestEvent",
        event_data={
            "test_field": "test_value",
            "timestamp": datetime.utcnow().isoformat()
        },
        occurred_at=datetime.utcnow()
    )


class TestEventBus:
    """事件总线测试"""
    
    async def test_publish_single_event(self, event_bus, sample_event):
        """测试发布单个事件"""
        # 发布事件
        await event_bus.publish(sample_event)
        
        # 验证事件已存储
        stored_events = await event_bus.event_store.get_events_by_aggregate_id(
            sample_event.aggregate_id
        )
        assert len(stored_events) == 1
        assert stored_events[0].event_type == "TestEvent"
    
    async def test_publish_multiple_events(self, event_bus):
        """测试批量发布事件"""
        events = [
            TestDomainEvent(
                aggregate_id=uuid4(),
                event_type=f"TestEvent{i}",
                event_data={"index": i},
                occurred_at=datetime.utcnow()
            )
            for i in range(3)
        ]
        
        # 批量发布事件
        await event_bus.publish_batch(events)
        
        # 验证所有事件已存储
        for i, event in enumerate(events):
            stored_events = await event_bus.event_store.get_events_by_aggregate_id(
                event.aggregate_id
            )
            assert len(stored_events) == 1
            assert stored_events[0].event_type == f"TestEvent{i}"
    
    async def test_register_and_handle_event(self, event_bus, sample_event):
        """测试注册和处理事件"""
        handler = TestEventHandler()
        
        # 注册处理器
        event_bus.register_handler("TestEvent", handler)
        
        # 发布事件
        await event_bus.publish(sample_event)
        
        # 等待事件处理
        await asyncio.sleep(0.1)
        
        # 验证事件已被处理
        assert handler.handle_count == 1
        assert len(handler.handled_events) == 1
        assert handler.handled_events[0].event_type == "TestEvent"
    
    async def test_handler_error_handling(self, event_bus, sample_event):
        """测试处理器错误处理"""
        handler = TestEventHandler()
        handler.should_fail = True
        
        # 注册处理器
        event_bus.register_handler("TestEvent", handler)
        
        # 发布事件
        await event_bus.publish(sample_event)
        
        # 等待事件处理
        await asyncio.sleep(0.1)
        
        # 验证处理器被调用但失败
        assert handler.handle_count == 1
        assert len(handler.handled_events) == 0
    
    async def test_process_unprocessed_events(self, event_bus):
        """测试处理未处理的事件"""
        handler = TestEventHandler()
        
        # 先发布事件（此时没有处理器）
        event = TestDomainEvent(
            aggregate_id=uuid4(),
            event_type="TestEvent",
            event_data={"test": "data"},
            occurred_at=datetime.utcnow()
        )
        await event_bus.publish(event)
        
        # 注册处理器
        event_bus.register_handler("TestEvent", handler)
        
        # 处理未处理的事件
        processed_count = await event_bus.process_unprocessed_events()
        
        # 验证事件被处理
        assert processed_count == 1
        assert handler.handle_count == 1


class TestEventDrivenCoordinator:
    """事件驱动协调器测试"""
    
    async def test_coordinator_initialization(self, coordinator):
        """测试协调器初始化"""
        assert coordinator.is_initialized
        
        # 获取状态
        status = await coordinator.get_coordinator_status()
        assert "initialized" in status
        assert "registered_handlers" in status
        assert "timestamp" in status
    
    async def test_publish_event_through_coordinator(self, coordinator, sample_event):
        """测试通过协调器发布事件"""
        await coordinator.publish_event(sample_event)
        
        # 验证事件历史
        history = await coordinator.get_event_history(limit=1)
        assert len(history) == 1
        assert history[0].event_type == "TestEvent"
    
    async def test_register_handler_through_coordinator(self, coordinator, sample_event):
        """测试通过协调器注册处理器"""
        handler = TestEventHandler()
        
        # 注册处理器
        await coordinator.register_handler("TestEvent", handler)
        
        # 发布事件
        await coordinator.publish_event(sample_event)
        
        # 等待处理
        await asyncio.sleep(0.1)
        
        # 验证处理
        assert handler.handle_count == 1
    
    async def test_event_history_query(self, coordinator):
        """测试事件历史查询"""
        # 发布多个事件
        events = [
            TestDomainEvent(
                aggregate_id=uuid4(),
                event_type="HistoryTest",
                event_data={"index": i},
                occurred_at=datetime.utcnow()
            )
            for i in range(5)
        ]
        
        for event in events:
            await coordinator.publish_event(event)
        
        # 查询历史
        history = await coordinator.get_event_history(limit=3)
        assert len(history) == 3
        
        # 按类型查询
        type_history = await coordinator.get_event_history(
            event_type="HistoryTest",
            limit=10
        )
        assert len(type_history) == 5
    
    async def test_event_replay(self, coordinator):
        """测试事件重放"""
        handler = TestEventHandler()
        
        # 发布事件
        aggregate_id = uuid4()
        event = TestDomainEvent(
            aggregate_id=aggregate_id,
            event_type="ReplayTest",
            event_data={"test": "replay"},
            occurred_at=datetime.utcnow()
        )
        await coordinator.publish_event(event)
        
        # 注册处理器
        await coordinator.register_handler("ReplayTest", handler)
        
        # 重放事件
        await coordinator.replay_events(
            aggregate_id=aggregate_id,
            from_sequence=0
        )
        
        # 验证重放
        assert handler.handle_count >= 1


class TestGlobalFunctions:
    """全局函数测试"""
    
    @pytest.fixture(scope="class", autouse=True)
    async def setup_teardown_coordinator(self):
        """为整个测试类设置和清理协调器"""
        # 确保开始时没有协调器
        try:
            await shutdown_coordinator()
        except Exception:
            pass
        
        yield  # 测试运行
        
        # 清理
        try:
            await shutdown_coordinator()
        except Exception:
            pass
    
    @pytest.fixture
    async def memory_coordinator(self):
        """创建使用内存存储的协调器"""
        event_store = InMemoryEventStore()
        event_publisher = InMemoryEventPublisher()
        event_bus = EventBus(event_store, event_publisher)
        coordinator = EventDrivenCoordinator(
            event_store=event_store,
            event_publisher=event_publisher,
            event_bus=event_bus
        )
        await coordinator.initialize()
        yield coordinator
        await coordinator.shutdown()
    
    async def test_global_coordinator_lifecycle(self):
        """测试全局协调器生命周期"""
        # 获取协调器
        coordinator1 = await get_coordinator()
        coordinator2 = await get_coordinator()
        
        # 应该是同一个实例
        assert coordinator1 is coordinator2
        assert coordinator1.is_initialized
        
        # 关闭协调器
        await shutdown_coordinator()
        
        # 再次获取应该是新实例
        coordinator3 = await get_coordinator()
        assert coordinator3 is not coordinator1
    
    async def test_global_publish_event(self, memory_coordinator):
        """测试全局事件发布"""
        # 创建测试事件
        test_event = TestDomainEvent(
            aggregate_id=uuid4(),
            event_type="TestEvent",
            event_data={"test": "data"},
            occurred_at=datetime.utcnow()
        )
        
        # 发布事件
        await memory_coordinator.publish_event(test_event)
        
        # 验证事件已发布
        history = await memory_coordinator.get_event_history(limit=1)
        assert len(history) == 1
        assert history[0].event_type == "TestEvent"
    
    async def test_global_publish_events(self, memory_coordinator):
        """测试全局批量事件发布"""
        events = [
            TestDomainEvent(
                aggregate_id=uuid4(),
                event_type=f"BatchTest{i}",
                event_data={"index": i},
                occurred_at=datetime.utcnow()
            )
            for i in range(3)
        ]
        
        # 批量发布
        await memory_coordinator.publish_events(events)
        
        # 验证
        history = await memory_coordinator.get_event_history(limit=10)
        batch_events = [e for e in history if e.event_type.startswith("BatchTest")]
        assert len(batch_events) == 3
    
    async def test_global_register_handler(self, memory_coordinator):
        """测试全局处理器注册"""
        handler = TestEventHandler()
        
        # 注册处理器
        await memory_coordinator.register_handler("GlobalTest", handler)
        
        # 发布事件
        event = TestDomainEvent(
            aggregate_id=uuid4(),
            event_type="GlobalTest",
            event_data={"test": "global"},
            occurred_at=datetime.utcnow()
        )
        await memory_coordinator.publish_event(event)
        
        # 等待处理
        await asyncio.sleep(0.1)
        
        # 验证
        assert handler.handle_count == 1


class TestEventBusFactory:
    """事件总线工厂测试"""
    
    async def test_create_event_bus(self, event_bus):
        """测试创建事件总线"""
        bus = event_bus
        
        assert bus is not None
        assert hasattr(bus, 'event_store')
        assert hasattr(bus, 'event_publisher')
        
        # 验证事件总线基本功能
        assert callable(getattr(bus, 'publish', None))
        assert callable(getattr(bus, 'register_handler', None))


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])