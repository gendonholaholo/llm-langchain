"""Tests for RAG components."""

from app.schemas.waha import WahaWebhookPayload


class TestWahaSchema:
    def test_extract_phone_number(self):
        payload = WahaWebhookPayload(
            event="message",
            session="default",
            payload={"from": "6281234567890@c.us", "body": "Hello", "fromMe": False},
        )
        assert payload.extract_phone_number() == "6281234567890"

    def test_get_message_body(self):
        payload = WahaWebhookPayload(
            event="message",
            session="default",
            payload={"from": "6281234567890@c.us", "body": "Hello world", "fromMe": False},
        )
        assert payload.get_message_body() == "Hello world"

    def test_is_from_me(self):
        payload = WahaWebhookPayload(
            event="message",
            session="default",
            payload={"from": "6281234567890@c.us", "body": "Hello", "fromMe": True},
        )
        assert payload.is_from_me() is True

    def test_not_from_me(self):
        payload = WahaWebhookPayload(
            event="message",
            session="default",
            payload={"from": "6281234567890@c.us", "body": "Hello", "fromMe": False},
        )
        assert payload.is_from_me() is False

    def test_get_chat_id(self):
        payload = WahaWebhookPayload(
            event="message",
            session="default",
            payload={"from": "6281234567890@c.us", "body": "Hi", "fromMe": False},
        )
        assert payload.get_chat_id() == "6281234567890@c.us"

    def test_no_phone_number_without_c_us(self):
        payload = WahaWebhookPayload(
            event="message",
            session="default",
            payload={"from": "groupchat@g.us", "body": "Hi", "fromMe": False},
        )
        assert payload.extract_phone_number() == "groupchat@g.us"
