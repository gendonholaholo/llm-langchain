"""PII detection using regex patterns."""

import structlog

from app.constants import PII_PATTERNS

logger = structlog.get_logger(__name__)


def detect_pii(text: str) -> tuple[bool, str | None]:
    """Detect personally identifiable information in text.

    Returns (has_pii, reason_if_found).
    """
    found_types: list[str] = []

    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            found_types.append(pii_type)

    if found_types:
        reason = (
            "Please don't share sensitive personal information like "
            f"{', '.join(found_types)} in chat. "
            "We'll collect necessary details securely during the booking process."
        )
        logger.warning("pii.detected", types=found_types)
        return True, reason

    return False, None
