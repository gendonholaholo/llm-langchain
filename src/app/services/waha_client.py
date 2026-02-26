"""Async HTTP client for WAHA (WhatsApp HTTP API)."""

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class WahaClient:
    def __init__(self) -> None:
        self._base_url = settings.waha_api_url.rstrip("/")
        self._session = settings.waha_session
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if settings.waha_api_key:
            headers["Authorization"] = f"Bearer {settings.waha_api_key}"
        self._client = httpx.AsyncClient(base_url=self._base_url, headers=headers, timeout=30.0)

    async def send_text(self, chat_id: str, text: str) -> dict:
        """Send a text message to a WhatsApp chat."""
        payload = {
            "chatId": chat_id,
            "text": text,
            "session": self._session,
        }
        response = await self._client.post("/api/sendText", json=payload)
        response.raise_for_status()
        data: dict = response.json()
        logger.info("waha.send_text", chat_id=chat_id, text_length=len(text))
        return data

    async def send_seen(self, chat_id: str) -> None:
        """Mark a chat as seen/read."""
        payload = {"chatId": chat_id, "session": self._session}
        try:
            response = await self._client.post("/api/sendSeen", json=payload)
            response.raise_for_status()
        except httpx.HTTPError:
            logger.warning("waha.send_seen_failed", chat_id=chat_id)

    async def check_health(self) -> bool:
        """Check if WAHA is reachable."""
        try:
            response = await self._client.get("/api/sessions")
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def close(self) -> None:
        await self._client.aclose()
