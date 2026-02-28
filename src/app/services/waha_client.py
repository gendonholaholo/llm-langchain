"""Async HTTP client for WAHA (WhatsApp HTTP API)."""

import structlog

from app.core.config import settings
from app.core.exceptions import ExternalAPIError
from app.core.http_client import BaseHTTPClient

logger = structlog.get_logger(__name__)


class WahaClient:
    def __init__(self) -> None:
        self._base_url = settings.waha_api_url.rstrip("/")
        self._session = settings.waha_session
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if settings.waha_api_key:
            headers["Authorization"] = f"Bearer {settings.waha_api_key}"
        self._client = BaseHTTPClient(base_url=self._base_url, headers=headers)

    async def send_text(self, chat_id: str, text: str) -> dict:
        """Send a text message to a WhatsApp chat."""
        payload = {
            "chatId": chat_id,
            "text": text,
            "session": self._session,
        }
        response = await self._client.post(
            "/api/sendText", "waha.send_text", json=payload
        )
        data: dict = response.json()
        logger.info("waha.send_text", chat_id=chat_id, text_length=len(text))
        return data

    async def send_seen(self, chat_id: str) -> None:
        """Mark a chat as seen/read."""
        payload = {"chatId": chat_id, "session": self._session}
        try:
            await self._client.post("/api/sendSeen", "waha.send_seen", json=payload)
        except ExternalAPIError:
            logger.warning("waha.send_seen_failed", chat_id=chat_id)

    async def check_health(self) -> bool:
        """Check if WAHA is reachable."""
        try:
            response = await self._client.get("/api/sessions", "waha.health_check")
            return response.status_code == 200
        except ExternalAPIError:
            return False

    async def close(self) -> None:
        await self._client.close()

