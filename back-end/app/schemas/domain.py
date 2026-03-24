"""도메인 가용성 확인 요청/응답 스키마"""

from pydantic import BaseModel, Field


class DomainCheckRequest(BaseModel):
    domain_name: str = Field(..., description="확인할 도메인 (예: example.com)")


class DomainCheckResult(BaseModel):
    domain_name: str = Field(..., description="확인한 도메인")
    available: bool = Field(..., description="등록 가능 여부")
    message: str = Field(default="", description="상태 메시지 (예: 등록가능)")
    price: str | None = Field(default=None, description="등록 가격 (원)")
    promotion_price: str | None = Field(default=None, description="프로모션 가격 (원)")
