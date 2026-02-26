"""Shared test fixtures."""

from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.waha import WahaWebhookPayload


@pytest.fixture
def sample_waha_payload() -> dict:
    return {
        "event": "message",
        "session": "default",
        "payload": {
            "id": "msg123",
            "timestamp": 1700000000,
            "from": "6281234567890@c.us",
            "to": "6289876543210@c.us",
            "body": "Hello, I need help",
            "fromMe": False,
        },
    }


@pytest.fixture
def parsed_waha_payload(sample_waha_payload: dict) -> WahaWebhookPayload:
    return WahaWebhookPayload(**sample_waha_payload)


@pytest.fixture
def mock_waha_client():
    with patch("app.services.chat.WahaClient") as mock_cls:
        client = AsyncMock()
        client.send_text = AsyncMock(return_value={"id": "sent123"})
        client.send_seen = AsyncMock()
        client.close = AsyncMock()
        mock_cls.return_value = client
        yield client


@pytest.fixture
def mock_openai():
    with patch("app.agent.nodes._chat_llm") as mock_chat, patch(
        "app.agent.nodes._router_llm"
    ) as mock_router:
        mock_chat.ainvoke = AsyncMock()
        mock_router.ainvoke = AsyncMock()
        yield {"chat": mock_chat, "router": mock_router}
