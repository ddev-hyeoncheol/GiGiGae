import asyncpg

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_pool: asyncpg.Pool | None = None


def _parse_url(url: str) -> str:
    """SQLAlchemy 스킴을 asyncpg 호환 스킴으로 변환"""
    return url.replace("postgresql+asyncpg://", "postgresql://")


async def init_pool() -> None:
    """asyncpg 커넥션 풀 생성 (앱 시작 시 1회 호출)"""
    global _pool

    if not settings.database_url:
        logger.info("Database: 미설정 (Mock 모드)")
        return

    try:
        _pool = await asyncpg.create_pool(
            _parse_url(settings.database_url),
            min_size=2,
            max_size=10,
        )
        logger.info("Database: 커넥션 풀 생성 완료")
    except Exception as e:
        logger.error(f"Database: 커넥션 풀 생성 실패 - {e}")
        _pool = None


async def close_pool() -> None:
    """커넥션 풀 종료 (앱 종료 시 1회 호출)"""
    global _pool

    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database: 커넥션 풀 종료")


def get_pool() -> asyncpg.Pool | None:
    """현재 커넥션 풀 반환 (DI용)"""
    return _pool
