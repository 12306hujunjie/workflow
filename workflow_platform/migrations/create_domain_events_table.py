"""创建领域事件表的数据库迁移脚本

这个脚本用于创建 domain_events 表，用于存储事件驱动架构中的所有领域事件。
"""

import asyncio
import logging
from sqlalchemy import text
from shared_kernel.infrastructure.database.async_session import db_config
from shared_kernel.infrastructure.database.models import DomainEventModel, Base

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def create_domain_events_table():
    """创建领域事件表"""
    try:
        logger.info("Starting domain events table creation...")
        
        # 获取异步引擎
        engine = db_config.engine
        
        # 创建所有表（包括 domain_events 表）
        async with engine.begin() as conn:
            # 创建表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Domain events table created successfully")
            
            # 验证表是否创建成功
            result = await conn.execute(
                text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'domain_events'
                """)
            )
            
            table_exists = result.fetchone()
            if table_exists:
                logger.info("Verified: domain_events table exists")
            else:
                logger.error("Failed to create domain_events table")
                return False
            
            # 验证索引是否创建成功
            result = await conn.execute(
                text("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = 'domain_events'
                """)
            )
            
            indexes = result.fetchall()
            logger.info(f"Created indexes: {[idx[0] for idx in indexes]}")
            
        logger.info("Domain events table migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create domain events table: {e}")
        raise
    finally:
        # 关闭引擎
        await engine.dispose()


async def drop_domain_events_table():
    """删除领域事件表（用于回滚）"""
    try:
        logger.info("Starting domain events table deletion...")
        
        # 获取异步引擎
        engine = db_config.engine
        
        async with engine.begin() as conn:
            # 删除表
            await conn.execute(text("DROP TABLE IF EXISTS domain_events CASCADE"))
            logger.info("Domain events table dropped successfully")
            
        logger.info("Domain events table rollback completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to drop domain events table: {e}")
        raise
    finally:
        # 关闭引擎
        await engine.dispose()


async def check_table_status():
    """检查表状态"""
    try:
        logger.info("Checking domain events table status...")
        
        # 获取异步引擎
        engine = db_config.engine
        
        async with engine.begin() as conn:
            # 检查表是否存在
            result = await conn.execute(
                text("""
                    SELECT 
                        table_name,
                        table_schema
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'domain_events'
                """)
            )
            
            table_info = result.fetchone()
            if table_info:
                logger.info(f"Table exists: {table_info[0]} in schema {table_info[1]}")
                
                # 获取表结构信息
                result = await conn.execute(
                    text("""
                        SELECT 
                            column_name,
                            data_type,
                            is_nullable,
                            column_default
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = 'domain_events'
                        ORDER BY ordinal_position
                    """)
                )
                
                columns = result.fetchall()
                logger.info("Table structure:")
                for col in columns:
                    logger.info(f"  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
                
                # 获取索引信息
                result = await conn.execute(
                    text("""
                        SELECT 
                            indexname,
                            indexdef
                        FROM pg_indexes 
                        WHERE tablename = 'domain_events'
                        ORDER BY indexname
                    """)
                )
                
                indexes = result.fetchall()
                logger.info("Table indexes:")
                for idx in indexes:
                    logger.info(f"  {idx[0]}: {idx[1]}")
                
                # 获取表统计信息
                result = await conn.execute(
                    text("""
                        SELECT 
                            schemaname,
                            tablename,
                            n_tup_ins as inserts,
                            n_tup_upd as updates,
                            n_tup_del as deletes,
                            n_live_tup as live_tuples,
                            n_dead_tup as dead_tuples
                        FROM pg_stat_user_tables 
                        WHERE tablename = 'domain_events'
                    """)
                )
                
                stats = result.fetchone()
                if stats:
                    logger.info(f"Table statistics: {dict(zip(['schema', 'table', 'inserts', 'updates', 'deletes', 'live_tuples', 'dead_tuples'], stats))}")
                
            else:
                logger.info("Table does not exist")
                
        return table_info is not None
        
    except Exception as e:
        logger.error(f"Failed to check table status: {e}")
        raise
    finally:
        # 关闭引擎
        await engine.dispose()


async def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python create_domain_events_table.py [create|drop|status]")
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "create":
            success = await create_domain_events_table()
            if success:
                print("✅ Domain events table created successfully")
            else:
                print("❌ Failed to create domain events table")
                
        elif command == "drop":
            success = await drop_domain_events_table()
            if success:
                print("✅ Domain events table dropped successfully")
            else:
                print("❌ Failed to drop domain events table")
                
        elif command == "status":
            exists = await check_table_status()
            if exists:
                print("✅ Domain events table exists and is properly configured")
            else:
                print("❌ Domain events table does not exist")
                
        else:
            print(f"Unknown command: {command}")
            print("Available commands: create, drop, status")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())