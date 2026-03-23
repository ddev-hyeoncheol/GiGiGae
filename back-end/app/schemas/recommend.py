from pydantic import BaseModel, Field


class BrandRequest(BaseModel):
    user_idea: str = Field(
        ..., max_length=250, description="사용자 아이디어 (250자 이내)"
    )
    industry: str = Field(..., description="산업 분야")
    exclude: list[str] = Field(
        default=[], description="제외할 브랜드명 목록 (재추천 시)"
    )


class BrandCandidate(BaseModel):
    name: str = Field(..., description="추천 브랜드명. 영문이면 영문, 한글이면 한글 (예: Brandium, 솜솜)")
    tags: list[str] = Field(
        ..., description="형용사형 특성 태그 2~3개 (예: 감각적인, 친근한, 혁신적인)"
    )


class BrandResponse(BaseModel):
    candidates: list[BrandCandidate]


class LogoRequest(BaseModel):
    selected_name: str = Field(..., description="선택한 브랜드명")


class LogoUrl(BaseModel):
    url: str = Field(..., description="로고 이미지 경로")
    style: str | None = Field(None, description="로고 스타일 설명")


class LogoResponse(BaseModel):
    logos: list[LogoUrl]


class DomainRequest(BaseModel):
    selected_name: str = Field(..., description="선택한 브랜드명")
    exclude: list[str] = Field(default=[], description="제외할 도메인 목록 (재추천 시)")


class DomainCandidate(BaseModel):
    domain: str = Field(..., description="추천 도메인 (예: volcaglow.com)")
    reason: str = Field(..., description="추천 이유 (한 문장, 형용사형 표현 권장)")


class DomainResponse(BaseModel):
    domains: list[DomainCandidate]
