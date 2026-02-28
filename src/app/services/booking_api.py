"""External booking API client."""

import structlog

from app.core.config import settings
from app.core.http_client import BaseHTTPClient
from app.schemas.booking import BookingRequest, BookingResponse

logger = structlog.get_logger(__name__)


class BookingAPIClient:
    def __init__(self) -> None:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if settings.booking_api_key:
            headers["Authorization"] = f"Bearer {settings.booking_api_key}"
        self._client = BaseHTTPClient(base_url=settings.booking_api_url, headers=headers)

    async def create_booking(self, request: BookingRequest) -> BookingResponse:
        """Submit a booking to the external API."""
        response = await self._client.post(
            "/api/bookings", "booking_api.create", json=request.model_dump()
        )
        data = response.json()
        logger.info("booking_api.created", reference_id=data.get("reference_id"))
        return BookingResponse(**data)

    async def close(self) -> None:
        await self._client.close()

