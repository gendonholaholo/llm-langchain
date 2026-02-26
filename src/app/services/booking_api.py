"""External booking API client."""

import httpx
import structlog

from app.core.config import settings
from app.schemas.booking import BookingRequest, BookingResponse

logger = structlog.get_logger(__name__)


class BookingAPIClient:
    def __init__(self) -> None:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if settings.booking_api_key:
            headers["Authorization"] = f"Bearer {settings.booking_api_key}"
        self._client = httpx.AsyncClient(
            base_url=settings.booking_api_url, headers=headers, timeout=30.0
        )

    async def create_booking(self, request: BookingRequest) -> BookingResponse:
        """Submit a booking to the external API."""
        response = await self._client.post("/api/bookings", json=request.model_dump())
        response.raise_for_status()
        data = response.json()
        logger.info("booking_api.created", reference_id=data.get("reference_id"))
        return BookingResponse(**data)

    async def close(self) -> None:
        await self._client.aclose()
