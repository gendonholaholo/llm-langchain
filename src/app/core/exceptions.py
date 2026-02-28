"""Custom exceptions for the application."""


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, user_message: str | None = None) -> None:
        super().__init__(message)
        self.user_message = user_message or "Sorry, something went wrong. Please try again."


class RetryableError(AppException):
    """Error that should trigger a retry."""


class NonRetryableError(AppException):
    """Error that should not be retried."""


class ExternalAPIError(RetryableError):
    """External API call failed."""


class LLMError(RetryableError):
    """LLM call failed."""


class DatabaseError(RetryableError):
    """Database operation failed."""


class ValidationError(NonRetryableError):
    """Input validation failed."""


class RateLimitError(RetryableError):
    """Rate limit exceeded."""
