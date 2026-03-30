"""FastAPI dependency injection factories."""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session per request."""
    import app.db.session as _session_module  # late import to get updated global
    factory = _session_module.async_session_factory
    if factory is None:
        raise RuntimeError("Database not initialized. Ensure lifespan startup ran.")
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_settings_dep() -> Settings:
    return get_settings()


SettingsDep = Depends(get_settings_dep)
DBSessionDep = Depends(get_db)
