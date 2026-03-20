import logging
import sys

from app.core.config import settings


def get_logger(name: str) -> logging.Logger:
    """모듈별 공통 Logger 인스턴스 생성"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(levelname)s: %(asctime)s - %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    return logger
