"""Pydantic models for WAHA webhook payloads."""

from typing import Any

from pydantic import BaseModel, Field


class WahaMessageKey(BaseModel):
    remote_jid: str = Field(alias="remoteJid")
    from_me: bool = Field(alias="fromMe")
    id: str


class WahaMessage(BaseModel):
    id: str
    timestamp: int
    from_: str = Field(alias="from")
    to: str
    body: str
    has_media: bool = Field(default=False, alias="hasMedia")


class WahaWebhookPayload(BaseModel):
    event: str
    session: str
    payload: dict[str, Any]

    def get_message_body(self) -> str | None:
        return self.payload.get("body")

    def get_chat_id(self) -> str | None:
        return self.payload.get("from")

    def is_from_me(self) -> bool:
        return bool(self.payload.get("fromMe", False))

    def extract_phone_number(self) -> str | None:
        chat_id = self.get_chat_id()
        if chat_id and "@c.us" in chat_id:
            return chat_id.replace("@c.us", "")
        return chat_id
