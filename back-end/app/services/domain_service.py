"""도메인 가용성 확인 비즈니스 로직"""

from app.plugins.nhn_domain_plugin import NhnDomainPlugin
from app.schemas.domain import DomainCheckResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DomainService:
    """도메인 가용성 확인 서비스"""

    def __init__(self, nhn_domain: NhnDomainPlugin):
        self._nhn_domain = nhn_domain

    async def check(self, domain_name: str) -> DomainCheckResult:
        """단건 도메인 가용성 확인"""
        logger.info(f"[Domain Check] domain='{domain_name}'")
        return await self._nhn_domain.check_availability(domain_name)
