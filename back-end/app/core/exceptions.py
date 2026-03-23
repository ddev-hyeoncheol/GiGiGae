from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 400,
        detail: str | None = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.detail = detail


class LLMTimeoutError(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            error_code="LLM_TIMEOUT",
            message="LLM 서비스 응답 시간이 초과되었습니다.",
            status_code=504,
            detail=detail,
        )


class LLMGenerationError(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            error_code="LLM_GENERATION_ERROR",
            message="LLM 응답 생성 중 오류가 발생했습니다.",
            status_code=502,
            detail=detail,
        )


class ExternalAPIError(AppException):
    def __init__(
        self,
        message: str = "외부 서비스 호출 중 오류가 발생했습니다.",
        detail: str | None = None,
    ):
        super().__init__(
            error_code="EXTERNAL_API_ERROR",
            message=message,
            status_code=502,
            detail=detail,
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """AppException을 규격화된 JSON 에러 응답으로 변환"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "detail": exc.detail,
        },
    )
