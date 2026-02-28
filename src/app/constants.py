"""Application constants, enums, and limits."""

import re
from enum import StrEnum


class ModelName(StrEnum):
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    EMBEDDING = "text-embedding-3-small"


class Intent(StrEnum):
    GREETING = "greeting"
    FAQ = "faq"
    PRODUCT_INQUIRY = "product_inquiry"
    BOOKING = "booking"
    GENERAL = "general"
    OFF_TOPIC = "off_topic"
    BLOCKED = "blocked"


class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class BookingStep(StrEnum):
    IDLE = "idle"
    COLLECTING_SERVICE = "collecting_service"
    COLLECTING_DATE = "collecting_date"
    COLLECTING_TIME = "collecting_time"
    COLLECTING_NAME = "collecting_name"
    CONFIRMING = "confirming"
    SUBMITTING = "submitting"
    COMPLETED = "completed"


class WahaEventType(StrEnum):
    MESSAGE = "message"
    MESSAGE_ACK = "message.ack"
    SESSION_STATUS = "session.status"


# Limits
MAX_HISTORY_MESSAGES = 20
MAX_RAG_RESULTS = 5
MAX_MESSAGE_LENGTH = 4000
CONVERSATION_TIMEOUT_HOURS = 24
EMBEDDING_DIMENSIONS = 1536

# Retry configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_MIN_WAIT_SECONDS = 1
RETRY_MAX_WAIT_SECONDS = 10
HTTP_TIMEOUT_SECONDS = 30.0
LLM_TIMEOUT_SECONDS = 60.0

# PII patterns (Indonesian-focused)
PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "nik": re.compile(r"\b\d{16}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+62|62|0)8\d{8,12}\b"),
}

ALLOWED_TOPICS = [
    "product information",
    "booking",
    "scheduling",
    "pricing",
    "services",
    "company information",
    "customer support",
    "faq",
    "greeting",
    "thank you",
    "feedback",
]
