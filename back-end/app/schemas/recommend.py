"""브랜드/도메인 추천 요청/응답 스키마"""

from pydantic import BaseModel, Field

from app.schemas.trademark import TrademarkSearchResponse


class BrandRecommendRequest(BaseModel):
    brand_idea: str = Field(
        ..., max_length=250, description="브랜드 아이디어 (250자 이내)"
    )
    brand_category: str | None = Field(default=None, description="브랜드 카테고리")
    exclude: list[str] = Field(
        default=[], description="제외할 브랜드명 목록 (재추천 시)"
    )


class BrandRecommendCandidate(BaseModel):
    """LLM 반환용 스키마"""

    brand_name: str = Field(
        ...,
        description="추천 브랜드명. 영문이면 영문, 한글이면 한글 (예: Brandium, 솜솜)",
    )
    brand_tags: list[str] = Field(
        ..., description="특성 태그 2~3개 (예: 감각적인, 친근한, 혁신적인)"
    )


class BrandRecommendLLMResponse(BaseModel):
    """LLM 반환용 응답 스키마"""

    brand_candidates: list[BrandRecommendCandidate]


class BrandRecommendResult(BaseModel):
    """API 응답용 스키마 (추천 + 상표 검색 결과)"""

    brand_name: str = Field(..., description="추천 브랜드명")
    brand_tags: list[str] = Field(..., description="특성 태그")
    trademark: TrademarkSearchResponse = Field(..., description="상표 검색 결과")


class BrandRecommendResponse(BaseModel):
    """최종 API 응답"""

    brand_candidates: list[BrandRecommendResult]


class DomainRecommendRequest(BaseModel):
    brand_name: str = Field(..., description="선택한 브랜드명")
    exclude: list[str] = Field(default=[], description="제외할 도메인 목록 (재추천 시)")


class DomainRecommendCandidate(BaseModel):
    domain_name: str = Field(..., description="추천 도메인 (예: volcaglow.com)")
    domain_reason: str = Field(..., description="추천 이유 (한 문장으로 간결하게)")


class DomainRecommendResponse(BaseModel):
    domain_candidates: list[DomainRecommendCandidate]
