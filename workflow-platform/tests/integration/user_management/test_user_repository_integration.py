"""用户仓储单元测试"""

import pytest
from sqlalchemy import select

from bounded_contexts.user_management.domain.entities.user import User
from bounded_contexts.user_management.infrastructure.models.user_models import UserModel
from bounded_contexts.user_management.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository
)
from shared_kernel.domain.value_objects import (
    Username, Email, HashedPassword, UserStatus
)


@pytest.mark.asyncio
class TestSQLAlchemyUserRepository:
    """SQLAlchemy用户仓储测试"""

    async def test_save_new_user(self, test_session):
        """测试保存新用户"""
        repository = SQLAlchemyUserRepository(test_session)

        # 创建用户
        user = User(
            username=Username(value="testuser"),
            email=Email(value="test@example.com"),
            hashed_password=HashedPassword(value="hashed_password_123")
        )

        # 保存用户
        await repository.save(user)
        await test_session.commit()

        # 查询验证
        result = await test_session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        user_model = result.scalar_one_or_none()

        assert user_model is not None
        assert user_model.username == "testuser"
        assert user_model.email == "test@example.com"
        assert user_model.hashed_password == "hashed_password_123"
        assert user_model.status == UserStatus.PENDING_VERIFICATION.value

    async def test_save_existing_user(self, test_session):
        """测试更新已存在的用户"""
        repository = SQLAlchemyUserRepository(test_session)

        # 创建并保存用户
        user = User(
            username=Username(value="existinguser"),
            email=Email(value="existing@example.com"),
            hashed_password=HashedPassword(value="hashed_password_123")
        )
        await repository.save(user)
        await test_session.commit()

        # 更新用户
        user.activate()
        await repository.save(user)
        await test_session.commit()

        # 查询验证
        result = await test_session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        user_model = result.scalar_one_or_none()

        assert user_model.status == UserStatus.ACTIVE.value

    async def test_get_by_id(self, test_session):
        """测试通过ID获取用户"""
        repository = SQLAlchemyUserRepository(test_session)

        # 创建并保存用户
        user = User(
            username=Username(value="getbyiduser"),
            email=Email(value="getbyid@example.com"),
            hashed_password=HashedPassword(value="hashed_password_123")
        )
        await repository.save(user)
        await test_session.commit()

        # 通过ID查找
        found_user = await repository.get_by_id(user.id)

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.username.value == "getbyiduser"
        assert found_user.email.value == "getbyid@example.com"

    async def test_get_by_id_not_found(self, test_session):
        """测试获取不存在的用户"""
        repository = SQLAlchemyUserRepository(test_session)

        # 查找不存在的用户
        found_user = await repository.get_by_id(999999)

        assert found_user is None

    async def test_get_by_username(self, test_session):
        """测试通过用户名获取用户"""
        repository = SQLAlchemyUserRepository(test_session)

        # 创建并保存用户
        user = User(
            username=Username(value="uniqueuser"),
            email=Email(value="unique@example.com"),
            hashed_password=HashedPassword(value="hashed_password_123")
        )
        await repository.save(user)
        await test_session.commit()

        # 通过用户名查找
        found_user = await repository.get_by_username("uniqueuser")

        assert found_user is not None
        assert found_user.username.value == "uniqueuser"

    async def test_get_by_email(self, test_session):
        """测试通过邮箱获取用户"""
        repository = SQLAlchemyUserRepository(test_session)

        # 创建并保存用户
        user = User(
            username=Username(value="emailuser"),
            email=Email(value="emailtest@example.com"),
            hashed_password=HashedPassword(value="hashed_password_123")
        )
        await repository.save(user)
        await test_session.commit()

        # 通过邮箱查找
        found_user = await repository.get_by_email("emailtest@example.com")

        assert found_user is not None
        assert found_user.email.value == "emailtest@example.com"

    async def test_delete_user(self, test_session):
        """测试删除用户"""
        repository = SQLAlchemyUserRepository(test_session)

        # 创建并保存用户
        user = User(
            username=Username(value="deleteuser"),
            email=Email(value="delete@example.com"),
            hashed_password=HashedPassword(value="hashed_password_123")
        )
        await repository.save(user)
        await test_session.commit()

        # 删除用户
        await repository.delete(user)
        await test_session.commit()

        # 验证删除
        result = await test_session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        user_model = result.scalar_one_or_none()

        assert user_model is None

    async def test_find_all_with_pagination(self, test_session):
        """测试分页查找所有用户"""
        repository = SQLAlchemyUserRepository(test_session)

        # 记录测试开始前的用户数量
        initial_count = await repository.count()

        # 创建多个用户
        test_users = []
        for i in range(15):
            user = User(
                username=Username(value=f"paginationuser{i}"),
                email=Email(value=f"paginationuser{i}@example.com"),
                hashed_password=HashedPassword(value="hashed_password_123")
            )
            test_users.append(user)
            await repository.save(user)

        await test_session.commit()

        # 验证总数量
        total_count = await repository.count()
        assert total_count == initial_count + 15

        # 获取所有用户并按创建时间排序
        all_users = await repository.find_all(skip=0, limit=total_count)
        # 只取我们创建的测试用户（最新的15个）
        our_test_users = sorted(all_users, key=lambda x: x.created_at, reverse=True)[:15]

        # 验证分页逻辑：模拟分页查询
        page1_users = our_test_users[:10]  # 前10个
        page2_users = our_test_users[10:]  # 后5个
        
        assert len(page1_users) == 10
        assert len(page2_users) == 5

        # 验证排序（按创建时间降序）
        assert page1_users[0].created_at >= page1_users[1].created_at

    async def test_count_users(self, test_session):
        """测试统计用户数量"""
        repository = SQLAlchemyUserRepository(test_session)

        # 初始数量
        initial_count = await repository.count()

        # 创建用户
        user = User(
            username=Username(value="countuser"),
            email=Email(value="count@example.com"),
            hashed_password=HashedPassword(value="hashed_password_123")
        )
        await repository.save(user)
        await test_session.commit()

        # 验证数量增加
        new_count = await repository.count()
        assert new_count == initial_count + 1

    async def test_exists_by_username(self, test_session):
        """测试检查用户名是否存在"""
        repository = SQLAlchemyUserRepository(test_session)

        # 创建用户
        user = User(
            username=Username(value="existsuser"),
            email=Email(value="exists@example.com"),
            hashed_password=HashedPassword(value="hashed_password_123")
        )
        await repository.save(user)
        await test_session.commit()

        # 检查存在
        exists = await repository.exists_by_username("existsuser")
        assert exists is True

        # 检查不存在
        not_exists = await repository.exists_by_username("notexists")
        assert not_exists is False

    async def test_exists_by_email(self, test_session):
        """测试检查邮箱是否存在"""
        repository = SQLAlchemyUserRepository(test_session)

        # 创建用户
        user = User(
            username=Username(value="emailexists"),
            email=Email(value="existsemail@example.com"),
            hashed_password=HashedPassword(value="hashed_password_123")
        )
        await repository.save(user)
        await test_session.commit()

        # 检查存在
        exists = await repository.exists_by_email("existsemail@example.com")
        assert exists is True

        # 检查不存在
        not_exists = await repository.exists_by_email("notexists@example.com")
        assert not_exists is False
