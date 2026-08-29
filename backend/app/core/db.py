"""
Postgres connection pool (asyncpg), with pgvector codec registration.

When DATABASE_URL is unset, every function is a no-op returning None — the
in-memory store in app.core.database stays the working fallback.
"""
import asyncpg
from pgvector.asyncpg import register_vector

from app.core.config import settings

_pool: asyncpg.Pool | None = None


async def _init_connection(conn: asyncpg.Connection) -> None:
    await register_vector(conn)


async def get_pool() -> asyncpg.Pool | None:
    """Return the shared connection pool, creating it lazily. None if DATABASE_URL is unset."""
    global _pool
    if not settings.DATABASE_URL:
        return None
    if _pool is None:
        _pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            init=_init_connection,
        )
    return _pool


async def health_check() -> bool:
    """True if the database is reachable. False (never raises) if unset or unreachable."""
    if not settings.DATABASE_URL:
        return False
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
