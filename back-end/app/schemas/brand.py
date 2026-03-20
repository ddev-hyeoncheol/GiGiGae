from typing import Literal

from pydantic import BaseModel, Field


class BrandRequest(BaseModel):
    user_idea: str = Field(..., max_length=250, description="사용자 아이디어 (250자 이내)")
    industry: str = Field(..., description="산업 분야")


class BrandCandidate(BaseModel):
    name: str = Field(..., description="추천 브랜드명")
    risk_level: Literal["Low", "High"] = Field(..., description="상표권 위험도")
    tags: list[str] = Field(..., description="브랜드 특성 태그 (예: 프리미엄, 자연친화)")


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


class DomainCandidate(BaseModel):
    domain: str = Field(..., description="추천 도메인 (예: volcaglow.com)")
    reason: str = Field(..., description="추천 이유 (짧게)")


class DomainResponse(BaseModel):
    domains: list[DomainCandidate]
