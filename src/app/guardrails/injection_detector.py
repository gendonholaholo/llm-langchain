"""Prompt injection detection using pattern matching."""

import re

import structlog

logger = structlog.get_logger(__name__)

INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?above\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+", re.IGNORECASE),
    re.compile(r"act\s+as\s+(a\s+)?DAN", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"DAN\s+mode", re.IGNORECASE),
    re.compile(r"developer\s+mode", re.IGNORECASE),
    re.compile(r"pretend\s+you\s+are", re.IGNORECASE),
    re.compile(r"system\s*prompt", re.IGNORECASE),
    re.compile(r"reveal\s+(your\s+)?instructions", re.IGNORECASE),
    re.compile(r"what\s+are\s+your\s+instructions", re.IGNORECASE),
    re.compile(r"override\s+(your\s+)?rules", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?rules", re.IGNORECASE),
    re.compile(r"new\s+instructions?\s*:", re.IGNORECASE),
    re.compile(r"\[system\]", re.IGNORECASE),
]


def detect_injection(text: str) -> tuple[bool, str | None]:
    """Detect prompt injection attempts.

    Returns (is_injection, reason_if_detected).
    """
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            logger.warning("injection.detected", pattern=pattern.pattern)
            return True, "Your message appears to contain an invalid request."

    return False, None
