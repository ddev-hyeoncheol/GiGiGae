"""브랜드/도메인 추천 비즈니스 로직"""

from app.core.constants import BRAND_CANDIDATE_COUNT

# 카테고리 → 니스 분류 코드 매핑
CATEGORY_NICE_MAP: dict[str, list[str]] = {
    "이커머스 · 온라인스토어": ["35", "42"],
    "F&B · 카페 · 숙박": ["29", "30", "32", "43"],
    "IT · SaaS · 테크": ["9", "42"],
    "패션 · 의류 브랜드": ["18", "25", "26"],
    "뷰티 · 코스메틱": ["3", "44"],
    "디지털 · 전자제품": ["11", "28"],
    "카페 · 베이커리 · 식품": ["29", "30", "31", "32"],
}


def resolve_nice_classes(categories: list[str] | None) -> list[str] | None:
    """카테고리 목록 → 중복 제거된 니스 분류 코드 리스트"""
    if not categories:
        return None
    codes: set[str] = set()
    for cat in categories:
        codes.update(CATEGORY_NICE_MAP.get(cat, []))
    return list(codes) if codes else None


from app.plugins.ollama_plugin import OllamaPlugin
from app.schemas.recommend import (
    BrandRecommendLLMResponse,
    BrandRecommendRequest,
    BrandRecommendResponse,
    BrandRecommendResult,
    DomainRecommendRequest,
    DomainRecommendResponse,
)
from app.services.trademark_service import TrademarkService
from app.utils.logger import get_logger
from app.utils.prompts import (
    BRAND_SYSTEM_PROMPT,
    DOMAIN_SYSTEM_PROMPT,
    build_brand_user_prompt,
    build_domain_user_prompt,
)

logger = get_logger(__name__)


class RecommendService:
    """브랜드 추천 비즈니스 로직 (LLM + 상표 검색 조합)"""

    def __init__(
        self,
        llm: OllamaPlugin,
        trademark: TrademarkService,
    ):
        self._llm = llm
        self._trademark = trademark

    async def recommend_brand(
        self, request: BrandRecommendRequest
    ) -> BrandRecommendResponse:
        """브랜드명 추천 + 상표 충돌 검색"""
        logger.info(
            f"[Recommend Brand] idea='{request.brand_idea}', "
            f"category={request.brand_category}, "
            f"tone={request.brand_tone}, "
            f"exclude={request.exclude}"
        )

        count = request.count if request.count is not None else BRAND_CANDIDATE_COUNT

        user_prompt = build_brand_user_prompt(
            brand_idea=request.brand_idea,
            brand_category=request.brand_category or None,
            brand_tone=request.brand_tone or None,
            count=count,
            exclude=request.exclude or None,
        )
        llm_result: BrandRecommendLLMResponse = await self._llm.generate(
            prompt=user_prompt,
            system_prompt=BRAND_SYSTEM_PROMPT,
            schema=BrandRecommendLLMResponse,
        )

        nice_classes = resolve_nice_classes(request.brand_category or None)

        async def _search_one(candidate):
            trademark_result = await self._trademark.search(
                brand_name=candidate.brand_name,
                nice_classes=nice_classes,
            )
            return BrandRecommendResult(
                brand_name=candidate.brand_name,
                brand_description=candidate.brand_description,
                brand_tags=candidate.brand_tags,
                trademark=trademark_result,
            )

        import asyncio
        brand_candidates = list(await asyncio.gather(
            *[_search_one(c) for c in llm_result.brand_candidates]
        ))

        return BrandRecommendResponse(brand_candidates=brand_candidates)

    async def recommend_domain(
        self, request: DomainRecommendRequest
    ) -> DomainRecommendResponse:
        """도메인 후보 추천"""
        logger.info(f"[Recommend Domain] name='{request.brand_name}'")
        user_prompt = build_domain_user_prompt(
            brand_name=request.brand_name,
            exclude=request.exclude or None,
        )
        return await self._llm.generate(
            prompt=user_prompt,
            system_prompt=DOMAIN_SYSTEM_PROMPT,
            schema=DomainRecommendResponse,
        )
