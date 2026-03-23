import asyncpg

from app.core.exceptions import ExternalAPIError
from app.schemas.trademark import TrademarkMatch, TrademarkSearchResponse
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

SEARCH_WITH_CLASS_SQL = """
    SELECT name, nice_class, legal_status, application_no,
           similarity(name, $1) AS score
    FROM trademarks
    WHERE similarity(name, $1) > $2
      AND legal_status = '등록'
      AND ({class_filter})
    ORDER BY score DESC
    LIMIT 10
"""


class TrademarkService:
    """pg_trgm 기반 상표 유사도 검색 서비스"""

    def __init__(self, pool: asyncpg.Pool | None = None):
        self._pool = pool

    async def search(
        self,
        brand_name: str,
        nice_classes: list[str] | None = None,
        threshold: float = 0.3,
    ) -> TrademarkSearchResponse:
        """브랜드명 유사 상표 검색"""
        if self._pool is None:
            return TrademarkSearchResponse(
                brand_name=brand_name, risk="unchecked", matches=[]
            )

        try:
            async with self._pool.acquire() as conn:
                if nice_classes:
                    conditions = [f"nice_class LIKE '%{cls}%'" for cls in nice_classes]
                    class_filter = " OR ".join(conditions)
                    query = SEARCH_WITH_CLASS_SQL.format(class_filter=class_filter)
                    rows = await conn.fetch(query, brand_name, threshold)
                else:
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

    @staticmethod
    def _evaluate_risk(matches: list[TrademarkMatch]) -> str:
        """최고 유사도 점수 기준 위험도 판별"""
        if not matches:
            return "Low"
        top_score = matches[0].similarity
        if top_score >= 0.7:
            return "High"
        elif top_score >= 0.4:
            return "Middle"
        return "Low"
