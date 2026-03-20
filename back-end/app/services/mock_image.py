from app.core.constants import MOCK_LOGO_STYLES
from app.schemas.brand import LogoUrl
from app.services.base_image import BaseImageService


class MockImageService(BaseImageService):
    async def generate_logos(self, brand_name: str, count: int = 4) -> list[LogoUrl]:
        """브랜드명 기반 Mock 로고 이미지 경로 생성"""
        logos = []
        for i in range(min(count, len(MOCK_LOGO_STYLES))):
            style = MOCK_LOGO_STYLES[i]
            logos.append(
                LogoUrl(
                    url=f"/static/mock/logo_{brand_name.lower().replace(' ', '_')}_{style}.png",
                    style=style,
                )
            )
        return logos
