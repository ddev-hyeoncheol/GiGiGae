from fastapi import APIRouter, Depends

from app.core.constants import BRAND_CANDIDATE_COUNT
from app.schemas.recommend import (
    BrandRequest,
    BrandResponse,
    DomainRequest,
    DomainResponse,
    LogoRequest,
    LogoResponse,
)
from app.services.base_image import BaseImageService
from app.services.base_llm import BaseLLMService
from app.utils.logger import get_logger
from app.utils.prompts import (
    BRAND_SYSTEM_PROMPT,
    DOMAIN_SYSTEM_PROMPT,
    build_brand_user_prompt,
    build_domain_user_prompt,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/recommend", tags=["recommend"])


def get_llm_service() -> BaseLLMService:
    """app_state에서 LLM 서비스 인스턴스 반환"""
    from app.main import app_state

    return app_state["llm_service"]


def get_image_service() -> BaseImageService:
    """app_state에서 Image 서비스 인스턴스 반환"""
    from app.main import app_state

    return app_state["image_service"]


@router.post("/brand", summary="브랜드명 추천", response_model=BrandResponse)
async def recommend_brand(
    request: BrandRequest,
    llm: BaseLLMService = Depends(get_llm_service),
):
    """사용자 아이디어 기반 브랜드명 후보 추천"""
    logger.info(
        f"[Recommend Brand] idea='{request.user_idea}', industry='{request.industry}'"
    )
    user_prompt = build_brand_user_prompt(
        user_idea=request.user_idea,
        industry=request.industry,
        count=BRAND_CANDIDATE_COUNT,
        exclude=request.exclude or None,
    )
    return await llm.generate(
        prompt=user_prompt,
        system_prompt=BRAND_SYSTEM_PROMPT,
        schema=BrandResponse,
    )


@router.post("/logo", summary="로고 후보 생성", response_model=LogoResponse)
async def recommend_logo(
    request: LogoRequest,
    image_service: BaseImageService = Depends(get_image_service),
):
    """선택된 브랜드명 기반 로고 후보 생성 (Mock)"""
    logger.info(f"[Recommend Logo] name='{request.selected_name}'")
    logos = await image_service.generate_logos(brand_name=request.selected_name)
    return LogoResponse(logos=logos)


@router.post("/domain", summary="도메인 후보 추천", response_model=DomainResponse)
async def recommend_domain(
    request: DomainRequest,
    llm: BaseLLMService = Depends(get_llm_service),
):
    """선택된 브랜드명 기반 도메인 후보 추천"""
    logger.info(f"[Recommend Domain] name='{request.selected_name}'")
    user_prompt = build_domain_user_prompt(
        brand_name=request.selected_name,
        exclude=request.exclude or None,
    )
    return await llm.generate(
        prompt=user_prompt,
        system_prompt=DOMAIN_SYSTEM_PROMPT,
        schema=DomainResponse,
    )
