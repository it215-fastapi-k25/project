import logging
from fastapi import Request, status
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


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.message, "details": exc.details, "data": None},
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "Internal server error", "details": None, "data": None},
    )