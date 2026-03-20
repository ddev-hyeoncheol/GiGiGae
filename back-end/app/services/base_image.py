from abc import ABC, abstractmethod

from app.schemas.brand import LogoUrl


class BaseImageService(ABC):
    @abstractmethod
    async def generate_logos(self, brand_name: str, count: int = 4) -> list[LogoUrl]:
        """브랜드명 기반 로고 이미지 생성 및 URL 목록 반환"""
        ...
