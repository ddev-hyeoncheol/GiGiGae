"""상표 검색 요청/응답 스키마"""

from pydantic import BaseModel, Field


class TrademarkSearchRequest(BaseModel):
    brand_name: str = Field(..., description="검색할 브랜드명")
    nice_classes: list[str] = Field(
        default=[], description="니스분류 필터 (예: ['35', '43'])"
    )
    threshold: float = Field(
        default=0.3, ge=0.0, le=1.0, description="유사도 임계값 (0~1)"
    )


class TrademarkMatch(BaseModel):
    name: str = Field(..., description="유사 상표명")
    nice_class: str | None = Field(None, description="니스분류 (파이프 구분)")
    legal_status: str | None = Field(None, description="법적상태")
    application_no: str = Field(..., description="출원번호")
    similarity: float = Field(..., description="유사도 점수 (0~1)")
    image_path: str | None = Field(None, description="상표 이미지 경로")


class TrademarkSearchResponse(BaseModel):
    brand_name: str = Field(..., description="검색한 브랜드명")
    risk: str = Field(..., description="충돌 위험도 (Low / Middle / High / unchecked)")
    matches: list[TrademarkMatch] = Field(default=[], description="유사 상표 목록")


class ImageSearchMatch(BaseModel):
    name: str = Field(..., description="상표명")
    nice_class: str | None = Field(None, description="니스분류")
    legal_status: str | None = Field(None, description="법적상태")
    application_no: str = Field(..., description="출원번호")
    similarity: float = Field(..., description="코사인 유사도 (0~1)")
    image_path: str | None = Field(None, description="상표 이미지 경로")


class ImageSearchResponse(BaseModel):
    matches: list[ImageSearchMatch] = Field(default=[], description="이미지 유사 상표 목록")
