"""O&G Agentic Canvas - Database Session Management."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


settings = get_settings()

from sqlalchemy.pool import NullPool

engine_kwargs = {"echo": settings.database_echo}
if settings.is_testing:
    engine_kwargs.update({"poolclass": NullPool})
elif not settings.database_url.startswith("sqlite"):
    engine_kwargs.update({"pool_pre_ping": True, "pool_size": 10, "max_overflow": 20})
else:
    engine_kwargs.update({
        "poolclass": NullPool,
        "connect_args": {"timeout": 30.0, "check_same_thread": False},
    })

engine = create_async_engine(settings.database_url, **engine_kwargs)


async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
