"""브랜드/도메인 추천 API 엔드포인트"""

from fastapi import APIRouter, Depends

from app.core.database import get_pool
from app.schemas.recommend import (
    BrandRecommendRequest,
    BrandRecommendResponse,
    DomainRecommendRequest,
    DomainRecommendResponse,
)
from app.services.recommend_service import RecommendService
from app.services.trademark_service import TrademarkService

router = APIRouter(prefix="/recommend", tags=["recommend"])


def get_recommend_service() -> RecommendService:
    """RecommendService DI"""
    from app.main import app_state

    return RecommendService(
        llm=app_state["llm"],
        trademark=TrademarkService(pool=get_pool()),
    )


@router.post("/brand", summary="브랜드명 추천", response_model=BrandRecommendResponse)
async def recommend_brand(
    request: BrandRecommendRequest,
    service: RecommendService = Depends(get_recommend_service),
):
    """사용자 아이디어 기반 브랜드명 후보 추천 + 상표 충돌 검색"""
    return await service.recommend_brand(request)


@router.post(
    "/domain", summary="도메인 후보 추천", response_model=DomainRecommendResponse
)
async def recommend_domain(
    request: DomainRecommendRequest,
    service: RecommendService = Depends(get_recommend_service),
):
    """선택된 브랜드명 기반 도메인 후보 추천"""
    return await service.recommend_domain(request)
