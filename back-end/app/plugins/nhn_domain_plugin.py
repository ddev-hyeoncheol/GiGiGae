"""NHN Cloud Domain API 플러그인"""

import httpx

from app.core.config import settings
from app.core.exceptions import ExternalAPIError
from app.schemas.domain import DomainCheckResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NhnDomainPlugin:
    """NHN Cloud 도메인 가용성 확인 클라이언트"""

    def __init__(
        self,
        api_url: str | None = None,
        timeout: int | None = None,
    ):
        self.api_url = api_url or settings.nhn_domain_api_url
        self.timeout = httpx.Timeout(timeout or settings.nhn_domain_timeout)

    async def check_availability(self, domain_name: str) -> DomainCheckResult:
        """도메인 등록 가능 여부 확인"""
        logger.info(f"[NHN Domain] Checking: {domain_name}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    data={"domain_name": domain_name},
                )
                response.raise_for_status()
                data = response.json()

            resp = data.get("response", {})
            price_info = data.get("price", {})

            available = resp.get("code") == "32000"
            message = resp.get("msg", "")

            price = None
            promotion_price = None
            if price_info and isinstance(price_info, dict):
                raw_price = price_info.get("newPrice")
                raw_promo = price_info.get("newPromotionPrice")
                if raw_price:
                    price = f"{int(raw_price):,}원"
                if raw_promo:
                    promotion_price = f"{int(raw_promo):,}원"

            return DomainCheckResult(
                domain_name=domain_name,
                available=available,
                message=message,
                price=price,
                promotion_price=promotion_price,
            )

        except (TimeoutError, httpx.TimeoutException) as e:
            logger.error(f"[NHN Domain Timeout] {domain_name}: {e}")
            raise ExternalAPIError(detail=f"NHN Domain API 타임아웃: {domain_name}")
        except Exception as e:
            logger.error(f"[NHN Domain Error] {domain_name}: {type(e).__name__}: {e}")
            raise ExternalAPIError(detail=f"NHN Domain API 오류: {domain_name}")
