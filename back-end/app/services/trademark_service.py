"""pg_trgm 기반 상표 유사도 검색 서비스 모듈"""

import asyncpg

from app.core.exceptions import ExternalAPIError
from app.schemas.trademark import (
    ImageSearchMatch,
    ImageSearchResponse,
    TrademarkMatch,
    TrademarkSearchResponse,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

SEARCH_SQL = """
    SELECT name, nice_class, legal_status, application_no,
           similarity(name, $1) AS score
    FROM trademarks
    WHERE similarity(name, $1) > $2
      AND legal_status = '등록'
    ORDER BY score DESC
    LIMIT 10
"""

IMAGE_SEARCH_SQL = """
    SELECT name, nice_class, legal_status, application_no, image_path,
           1 - (image_embedding <=> $1::vector) AS score
    FROM trademarks
    WHERE image_embedding IS NOT NULL
    ORDER BY image_embedding <=> $1::vector
    LIMIT $2
"""

SEARCH_WITH_CLASS_SQL = """
    SELECT name, nice_class, legal_status, application_no,
           similarity(name, $1) AS score
    FROM trademarks
    WHERE similarity(name, $1) > $2
      AND legal_status = '등록'
      AND nice_class LIKE ANY($3)
    ORDER BY score DESC
    LIMIT 10
"""


class TrademarkService:
    """pg_trgm 기반 상표 유사도 검색 서비스"""

    def __init__(self, pool: asyncpg.Pool | None = None):
        """pool이 None이면 Mock 모드로 동작"""
        self._pool = pool

    async def search(
        self,
        brand_name: str,
        nice_classes: list[str] | None = None,
        threshold: float = 0.3,
    ) -> TrademarkSearchResponse:
        """브랜드명으로 유사 상표를 검색하고 위험도를 판별"""
        if self._pool is None:
            return TrademarkSearchResponse(
                brand_name=brand_name, risk="unchecked", matches=[]
            )

        try:
            async with self._pool.acquire() as conn:
                rows = []
                if nice_classes:
                    patterns = [f"%{cls}%" for cls in nice_classes]
                    rows = await conn.fetch(
                        SEARCH_WITH_CLASS_SQL, brand_name, threshold, patterns
                    )
                # 폴백: 니스 필터 결과가 없으면 전체 검색
                if not rows:
                    rows = await conn.fetch(SEARCH_SQL, brand_name, threshold)

                matches = [
                    TrademarkMatch(
                        name=row["name"],
                        nice_class=row["nice_class"],
                        legal_status=row["legal_status"],
                        application_no=row["application_no"],
                        similarity=round(float(row["score"]), 4),
                    )
                    for row in rows
                ]

                risk = self._evaluate_risk(matches)
                return TrademarkSearchResponse(
                    brand_name=brand_name, risk=risk, matches=matches
                )

        except Exception as e:
            logger.error(f"TrademarkService: 검색 실패 - {e}")
            raise ExternalAPIError(
                message="상표 검색 중 오류가 발생했습니다.", detail=str(e)
            )

    async def search_by_image(
        self,
        embedding: list[float],
        limit: int = 10,
    ) -> ImageSearchResponse:
        """이미지 임베딩 벡터로 유사 상표 검색"""
        if self._pool is None:
            return ImageSearchResponse(matches=[])

        try:
            vec_str = "[" + ",".join(f"{v:.6f}" for v in embedding) + "]"
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(IMAGE_SEARCH_SQL, vec_str, limit)
                matches = [
                    ImageSearchMatch(
                        name=row["name"],
                        nice_class=row["nice_class"],
                        legal_status=row["legal_status"],
                        application_no=row["application_no"],
                        similarity=round(float(row["score"]), 4),
                        image_path=row["image_path"].replace(
                            "/data/image", "/image"
                        ) if row["image_path"] else None,
                    )
                    for row in rows
                ]
                return ImageSearchResponse(matches=matches)

        except Exception as e:
            logger.error(f"TrademarkService: 이미지 검색 실패 - {e}")
            raise ExternalAPIError(
                message="이미지 유사 상표 검색 중 오류가 발생했습니다.", detail=str(e)
            )

    @staticmethod
    def _evaluate_risk(matches: list[TrademarkMatch]) -> str:
        """최고 유사도 기준 위험도 판별 (High >= 0.55, Middle >= 0.4, Low)"""
        if not matches:
            return "Low"
        top_score = matches[0].similarity
        if top_score >= 0.55:
            return "High"
        elif top_score >= 0.4:
            return "Middle"
        return "Low"
