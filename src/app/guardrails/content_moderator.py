"""Content moderation using OpenAI Moderation API."""

import structlog
from openai import AsyncOpenAI

from app.core.config import settings

logger = structlog.get_logger(__name__)

_client = AsyncOpenAI(api_key=settings.openai_api_key)


async def check_content_moderation(text: str) -> tuple[bool, str | None]:
    """Check text against OpenAI Moderation API.

    Returns (is_safe, reason_if_blocked).
    """
    try:
        response = await _client.moderations.create(input=text)
        result = response.results[0]

        if result.flagged:
            flagged_categories = [
                cat for cat, flagged in result.categories.model_dump().items() if flagged
            ]
            reason = f"Content flagged for: {', '.join(flagged_categories)}"
            logger.warning("moderation.flagged", categories=flagged_categories)
            return False, reason

        return True, None

    except Exception:
        logger.exception("moderation.api_error")
        # Fail open: allow message through if moderation API is down
        return True, None
