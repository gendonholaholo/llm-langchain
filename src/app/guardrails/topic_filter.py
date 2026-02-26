"""LLM-based topic filtering."""

import structlog
from langchain_openai import ChatOpenAI

from app.agent.prompts import TOPIC_FILTER_PROMPT
from app.constants import ALLOWED_TOPICS, ModelName

logger = structlog.get_logger(__name__)

_filter_llm = ChatOpenAI(model=ModelName.GPT_4O_MINI, temperature=0, max_tokens=10)


async def check_topic(text: str) -> bool:
    """Check if the message is on-topic using LLM classification.

    Returns True if on-topic, False if off-topic.
    """
    try:
        prompt = TOPIC_FILTER_PROMPT.format(
            allowed_topics=", ".join(ALLOWED_TOPICS),
            message=text,
        )
        response = await _filter_llm.ainvoke(prompt)
        result = str(response.content).strip().lower()
        is_on_topic = "on_topic" in result
        if not is_on_topic:
            logger.info("topic_filter.off_topic", message_preview=text[:100])
        return is_on_topic
    except Exception:
        logger.exception("topic_filter.error")
        # Fail open
        return True
