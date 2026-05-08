"""Custom exception hierarchy — domain-aware errors mapped to HTTP codes."""
from typing import Any, Optional


class AppException(Exception):
    """Base application exception."""
    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppException):
    status_code = 404
    code = "not_found"


class ValidationError(AppException):
    status_code = 422
    code = "validation_error"


class UnauthorizedError(AppException):
    status_code = 401
    code = "unauthorized"


class ForbiddenError(AppException):
    status_code = 403
    code = "forbidden"


class ConflictError(AppException):
    status_code = 409
    code = "conflict"


class RateLimitedError(AppException):
    status_code = 429
    code = "rate_limited"


class ExternalServiceError(AppException):
    status_code = 503
    code = "external_service_unavailable"