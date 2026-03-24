"""도메인 가용성 확인 API 엔드포인트"""

from fastapi import APIRouter, Depends

from app.plugins.nhn_domain_plugin import NhnDomainPlugin
from app.schemas.domain import DomainCheckRequest, DomainCheckResult
from app.services.domain_service import DomainService

router = APIRouter(prefix="/domain", tags=["domain"])


def get_domain_service() -> DomainService:
    """DomainService DI"""
    from app.main import app_state

    return DomainService(nhn_domain=app_state["nhn_domain"])


@router.post("/check", summary="도메인 가용성 확인", response_model=DomainCheckResult)
async def check_domain(
    request: DomainCheckRequest,
    service: DomainService = Depends(get_domain_service),
):
    """NHN Cloud API를 통한 도메인 등록 가능 여부 확인"""
    return await service.check(request.domain_name)
