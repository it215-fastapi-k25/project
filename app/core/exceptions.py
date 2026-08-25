import logging
from datetime import datetime, timezone
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("app")


class AppException(Exception):
    def __init__(self, status_code: int, message: str, details: dict | None = None):
        self.status_code = status_code
        self.message = message
        self.details = details


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", details: dict | None = None):
        super().__init__(status.HTTP_404_NOT_FOUND, message, details)


class BadRequestException(AppException):
    def __init__(self, message: str = "Bad request", details: dict | None = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, details)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden", details: dict | None = None):
        super().__init__(status.HTTP_403_FORBIDDEN, message, details)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized", details: dict | None = None):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, details)


class ConflictException(AppException):
    def __init__(self, message: str = "Conflict", details: dict | None = None):
        super().__init__(status.HTTP_409_CONFLICT, message, details)


def build_envelope(status_code: int, message: str, path: str, data=None, error=None) -> dict:
    return {
        "statusCode": status_code,
        "message": message,
        "data": data,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": path,
    }


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=build_envelope(exc.status_code, exc.message, str(request.url.path), error=exc.details),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=build_envelope(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Validation error",
            str(request.url.path),
            error=exc.errors(),
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_envelope(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error", str(request.url.path)
        ),
    ) 
    
async def rate_limit_exceeded_handler(request: Request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=build_envelope(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many requests",
            str(request.url.path),
            error=str(exc.detail) if hasattr(exc, "detail") else str(exc),
        ),
    )