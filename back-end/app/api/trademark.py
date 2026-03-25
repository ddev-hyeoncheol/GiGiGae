"""상표 검색 API 엔드포인트"""

from fastapi import APIRouter, Depends, File, UploadFile
from PIL import Image
import io

from app.core.database import get_pool
from app.plugins.clip_plugin import ClipPlugin
from app.schemas.trademark import (
    ImageSearchResponse,
    TrademarkSearchRequest,
    TrademarkSearchResponse,
)
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


@router.post(
    "/image-search",
    summary="이미지 기반 유사 상표 검색",
    response_model=ImageSearchResponse,
)
async def search_trademark_by_image(
    file: UploadFile = File(..., description="로고 이미지 파일"),
    service: TrademarkService = Depends(get_trademark_service),
):
    """업로드한 로고 이미지와 시각적으로 유사한 등록 상표를 검색"""
    logger.info(f"[Trademark Image Search] filename={file.filename}")
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    clip_plugin = ClipPlugin.get()
    embedding = clip_plugin.embed_image(image)

    return await service.search_by_image(embedding=embedding, limit=10)
