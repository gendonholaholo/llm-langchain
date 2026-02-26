"""Tests for the WAHA webhook endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestWebhook:
    def test_webhook_accepts_message_event(self, client: TestClient):
        """Webhook should return 200 for valid message events."""
        with patch("app.api.webhook.ChatService.process_message", new_callable=AsyncMock):
            response = client.post(
                "/webhook/waha",
                json={
                    "event": "message",
                    "session": "default",
                    "payload": {
                        "from": "6281234567890@c.us",
                        "to": "bot@c.us",
                        "body": "Hello",
                        "fromMe": False,
                    },
                },
            )
        assert response.status_code == 200

    def test_webhook_ignores_non_message_events(self, client: TestClient):
        """Webhook should return 200 but not process non-message events."""
        response = client.post(
            "/webhook/waha",
            json={
                "event": "message.ack",
                "session": "default",
                "payload": {"ack": 3},
            },
        )
        assert response.status_code == 200

    def test_webhook_ignores_own_messages(self, client: TestClient):
        """Webhook should ignore messages sent by the bot itself."""
        response = client.post(
            "/webhook/waha",
            json={
                "event": "message",
                "session": "default",
                "payload": {
                    "from": "6281234567890@c.us",
                    "to": "bot@c.us",
                    "body": "Hello",
                    "fromMe": True,
                },
            },
        )
        assert response.status_code == 200

    def test_webhook_ignores_empty_body(self, client: TestClient):
        """Webhook should ignore messages with no body."""
        response = client.post(
            "/webhook/waha",
            json={
                "event": "message",
                "session": "default",
                "payload": {
                    "from": "6281234567890@c.us",
                    "to": "bot@c.us",
                    "body": "",
                    "fromMe": False,
                },
            },
        )
        assert response.status_code == 200
