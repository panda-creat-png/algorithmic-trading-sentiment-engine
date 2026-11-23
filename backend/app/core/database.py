import time
from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text, event
from app.core.config import settings
from app.core.logging import logger

# Configure connect_args depending on engine
connect_args: Dict[str, Any] = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    connect_args["timeout"] = 30

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

# Optimize SQLite for multi-reader multi-writer asynchronous concurrency
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB memory page cache
        cursor.close()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> Dict[str, Any]:
    """Tests the database connection and measures response latency."""
    start_time = time.perf_counter()
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            db_type = "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "SQLite"
            return {
                "status": "connected",
                "database_type": db_type,
                "latency_ms": latency_ms,
            }
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return {
            "status": "disconnected",
            "error": str(e),
            "latency_ms": None,
        }


async def init_db() -> None:
    """Creates all database tables defined in the ORM Base."""
    from app.models.base import Base
    # Import all models so Base has metadata registered
    import app.models  # noqa: F401
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schemas verified and initialized.")

