"""브랜드/도메인 추천 비즈니스 로직"""

from app.core.constants import BRAND_CANDIDATE_COUNT
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

        user_prompt = build_brand_user_prompt(
            brand_idea=request.brand_idea,
            brand_category=request.brand_category or None,
            brand_tone=request.brand_tone or None,
            count=BRAND_CANDIDATE_COUNT,
            exclude=request.exclude or None,
        )
        llm_result: BrandRecommendLLMResponse = await self._llm.generate(
            prompt=user_prompt,
            system_prompt=BRAND_SYSTEM_PROMPT,
            schema=BrandRecommendLLMResponse,
        )

        brand_candidates = []
        for candidate in llm_result.brand_candidates:
            trademark_result = await self._trademark.search(
                brand_name=candidate.brand_name
            )
            brand_candidates.append(
                BrandRecommendResult(
                    brand_name=candidate.brand_name,
                    brand_description=candidate.brand_description,
                    brand_tags=candidate.brand_tags,
                    trademark=trademark_result,
                )
            )

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
