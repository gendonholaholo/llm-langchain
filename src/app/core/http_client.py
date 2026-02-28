"""Base HTTP client with retry logic."""

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.constants import (
    HTTP_TIMEOUT_SECONDS,
    MAX_RETRY_ATTEMPTS,
    RETRY_MAX_WAIT_SECONDS,
    RETRY_MIN_WAIT_SECONDS,
)
from app.core.exceptions import ExternalAPIError, RateLimitError

logger = structlog.get_logger(__name__)


def create_retry_decorator(operation_name: str):
    """Create a retry decorator for HTTP operations."""

    def before_sleep(retry_state):
        logger.warning(
            f"{operation_name}.retry",
            attempt=retry_state.attempt_number,
            wait=retry_state.next_action.sleep,
        )

    return retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(
            min=RETRY_MIN_WAIT_SECONDS,
            max=RETRY_MAX_WAIT_SECONDS,
        ),
        before_sleep=before_sleep,
        reraise=True,
    )


class BaseHTTPClient:
    """Base HTTP client with retry and error handling."""

    def __init__(self, base_url: str, headers: dict[str, str] | None = None) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers or {},
            timeout=HTTP_TIMEOUT_SECONDS,
        )

    async def _request(
        self, method: str, url: str, operation_name: str, **kwargs
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""
        retry_decorator = create_retry_decorator(operation_name)

        @retry_decorator
        async def _do_request():
            try:
                response = await self._client.request(method, url, **kwargs)
                if response.status_code == 429:
                    raise RateLimitError(
                        f"Rate limit exceeded for {operation_name}",
                        "Service is busy. Please try again in a moment.",
                    )
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if 500 <= e.response.status_code < 600:
                    raise ExternalAPIError(
                        f"{operation_name} server error: {e}",
                        "Service temporarily unavailable. Please try again.",
                    )
                raise ExternalAPIError(
                    f"{operation_name} failed: {e}",
                    "Request failed. Please check your input and try again.",
                )
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                raise ExternalAPIError(
                    f"{operation_name} connection error: {e}",
                    "Connection failed. Please check your internet and try again.",
                )

        return await _do_request()

    async def get(self, url: str, operation_name: str, **kwargs) -> httpx.Response:
        return await self._request("GET", url, operation_name, **kwargs)

    async def post(self, url: str, operation_name: str, **kwargs) -> httpx.Response:
        return await self._request("POST", url, operation_name, **kwargs)

    async def close(self) -> None:
        await self._client.aclose()
