from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config import get_settings

settings = get_settings()

# Async engine — used by FastAPI request handlers
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

# Sync engine — used by Celery workers
sync_engine = create_engine(
    settings.database_url_sync,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
SyncSessionLocal = sessionmaker(sync_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_session() -> Session:
    return SyncSessionLocal()
