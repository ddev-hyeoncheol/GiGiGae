"""상표 검색 API 엔드포인트"""

from fastapi import APIRouter, Depends

from app.core.database import get_pool
from app.schemas.trademark import TrademarkSearchRequest, TrademarkSearchResponse
from app.services.trademark_service import TrademarkService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/trademark", tags=["trademark"])


def get_trademark_service() -> TrademarkService:
    """커넥션 풀을 주입받아 TrademarkService 생성"""
    return TrademarkService(pool=get_pool())


@router.post(
    "/search", summary="상표 유사도 검색", response_model=TrademarkSearchResponse
)
async def search_trademark(
    request: TrademarkSearchRequest,
    service: TrademarkService = Depends(get_trademark_service),
):
    """브랜드명에 대한 등록 상표 유사도 검색"""
    logger.info(
        f"[Trademark Search] brand_name='{request.brand_name}', "
        f"nice_classes={request.nice_classes}, threshold={request.threshold}"
    )
    return await service.search(
        brand_name=request.brand_name,
        nice_classes=request.nice_classes or None,
        threshold=request.threshold,
    )
