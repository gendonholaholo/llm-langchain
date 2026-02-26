"""LangGraph node functions for the agent pipeline."""

import structlog
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from app.agent.prompts import (
    BLOCKED_RESPONSE,
    BOOKING_COLLECT_PROMPT,
    RAG_RESPONSE_PROMPT,
    ROUTER_PROMPT,
    SYSTEM_PROMPT,
)
from app.agent.state import AgentState
from app.constants import BookingStep, Intent, ModelName
from app.guardrails.content_moderator import check_content_moderation
from app.guardrails.injection_detector import detect_injection
from app.guardrails.pii_detector import detect_pii
from app.guardrails.topic_filter import check_topic
from app.rag.retriever import retrieve_documents
from app.schemas.booking import BookingParams, BookingRequest
from app.services.booking_api import BookingAPIClient

logger = structlog.get_logger(__name__)

_router_llm = ChatOpenAI(model=ModelName.GPT_4O_MINI, temperature=0, max_tokens=20)
_chat_llm = ChatOpenAI(model=ModelName.GPT_4O, temperature=0.7, max_tokens=500)
_booking_llm = ChatOpenAI(model=ModelName.GPT_4O, temperature=0.3, max_tokens=500)


def _get_last_user_message(state: AgentState) -> str:
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            return str(msg.content)
    return ""


async def guardrails_node(state: AgentState) -> dict:
    """Run all guardrail checks on the incoming message."""
    user_msg = _get_last_user_message(state)

    # 1. Content moderation
    moderation_ok, mod_reason = await check_content_moderation(user_msg)
    if not moderation_ok:
        return {
            "guardrail_result": {"passed": False, "blocked_reason": mod_reason},
            "intent": Intent.BLOCKED,
        }

    # 2. Prompt injection detection
    injection_found, inj_reason = detect_injection(user_msg)
    if injection_found:
        return {
            "guardrail_result": {"passed": False, "blocked_reason": inj_reason},
            "intent": Intent.BLOCKED,
        }

    # 3. PII detection
    pii_found, pii_reason = detect_pii(user_msg)
    if pii_found:
        return {
            "guardrail_result": {"passed": False, "blocked_reason": pii_reason},
            "intent": Intent.BLOCKED,
        }

    # 4. Topic restriction
    topic_ok = await check_topic(user_msg)
    if not topic_ok:
        return {
            "guardrail_result": {"passed": False, "blocked_reason": "Message is off-topic."},
            "intent": Intent.OFF_TOPIC,
        }

    return {"guardrail_result": {"passed": True, "blocked_reason": None}}


async def router_node(state: AgentState) -> dict:
    """Classify user intent for routing."""
    user_msg = _get_last_user_message(state)
    prompt = ROUTER_PROMPT.format(message=user_msg)
    response = await _router_llm.ainvoke(prompt)
    raw_intent = str(response.content).strip().lower()

    try:
        intent = Intent(raw_intent)
    except ValueError:
        intent = Intent.GENERAL
        logger.warning("router.unknown_intent", raw=raw_intent)

    # Detect language from message
    detected_language = state.get("detected_language", "Indonesian")

    return {"intent": intent, "detected_language": detected_language}


async def blocked_response_node(state: AgentState) -> dict:
    """Generate a polite rejection for blocked messages."""
    reason = state["guardrail_result"].get("blocked_reason", "")
    response_text = BLOCKED_RESPONSE.format(reason=reason)
    return {"messages": [AIMessage(content=response_text)]}


async def general_respond_node(state: AgentState) -> dict:
    """Handle greetings and general conversation."""
    system = SYSTEM_PROMPT.format(detected_language=state.get("detected_language", "Indonesian"))
    messages = [{"role": "system", "content": system}, *_format_messages(state)]
    response = await _chat_llm.ainvoke(messages)
    return {"messages": [AIMessage(content=str(response.content))]}


async def rag_node(state: AgentState) -> dict:
    """Retrieve relevant documents for FAQ/product queries."""
    user_msg = _get_last_user_message(state)
    docs = await retrieve_documents(user_msg)
    return {"retrieved_docs": docs}


async def rag_respond_node(state: AgentState) -> dict:
    """Generate a response based on retrieved RAG documents."""
    user_msg = _get_last_user_message(state)
    context = "\n\n".join(state.get("retrieved_docs", []))
    if not context:
        context = "No relevant information found."

    prompt = RAG_RESPONSE_PROMPT.format(
        context=context,
        question=user_msg,
        detected_language=state.get("detected_language", "Indonesian"),
    )
    response = await _chat_llm.ainvoke(prompt)
    return {"messages": [AIMessage(content=str(response.content))]}


async def booking_node(state: AgentState) -> dict:
    """Handle booking conversation flow."""
    user_msg = _get_last_user_message(state)
    booking_params = state.get("booking_params", {})
    booking_step = state.get("booking_step", BookingStep.IDLE)

    # Parse the current step and extract info from user message
    params = BookingParams(**booking_params)

    if booking_step == BookingStep.IDLE:
        booking_step = BookingStep.COLLECTING_SERVICE
    elif booking_step == BookingStep.COLLECTING_SERVICE and user_msg:
        params.service_type = user_msg
        booking_step = BookingStep.COLLECTING_DATE
    elif booking_step == BookingStep.COLLECTING_DATE and user_msg:
        params.preferred_date = user_msg
        booking_step = BookingStep.COLLECTING_TIME
    elif booking_step == BookingStep.COLLECTING_TIME and user_msg:
        params.preferred_time = user_msg
        booking_step = BookingStep.COLLECTING_NAME
    elif booking_step == BookingStep.COLLECTING_NAME and user_msg:
        params.customer_name = user_msg
        params.customer_phone = state.get("phone_number", "")
        booking_step = BookingStep.CONFIRMING

    prompt = BOOKING_COLLECT_PROMPT.format(
        booking_params=params.model_dump_json(indent=2),
        booking_step=booking_step,
        detected_language=state.get("detected_language", "Indonesian"),
    )
    response = await _booking_llm.ainvoke(prompt)

    return {
        "messages": [AIMessage(content=str(response.content))],
        "booking_params": params.model_dump(),
        "booking_step": booking_step,
    }


def booking_check_route(state: AgentState) -> str:
    """Determine next step in booking flow."""
    step = state.get("booking_step", BookingStep.IDLE)
    if step == BookingStep.CONFIRMING:
        user_msg = _get_last_user_message(state).lower()
        if any(w in user_msg for w in ("yes", "ya", "confirm", "ok", "oke", "setuju")):
            return "submit"
    if step == BookingStep.COMPLETED:
        return "done"
    return "continue"


async def submit_booking_node(state: AgentState) -> dict:
    """Submit the booking to the external API."""
    params = state.get("booking_params", {})
    request = BookingRequest(
        service_type=params.get("service_type", ""),
        preferred_date=params.get("preferred_date", ""),
        preferred_time=params.get("preferred_time", ""),
        customer_name=params.get("customer_name", ""),
        customer_phone=params.get("customer_phone", state.get("phone_number", "")),
    )

    client = BookingAPIClient()
    try:
        result = await client.create_booking(request)
        if result.success:
            text = (
                f"Booking confirmed! Your reference ID is: {result.reference_id}\n"
                f"We'll send you a reminder before your appointment."
            )
        else:
            text = f"Sorry, the booking could not be completed: {result.message}"
    except Exception:
        logger.exception("booking.submit_failed")
        text = "Sorry, there was an error processing your booking. Please try again later."
    finally:
        await client.close()

    return {
        "messages": [AIMessage(content=text)],
        "booking_step": BookingStep.COMPLETED,
    }


def _format_messages(state: AgentState) -> list[dict[str, str]]:
    """Convert state messages to dict format for LLM."""
    result = []
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            result.append({"role": "user", "content": str(msg.content)})
        elif isinstance(msg, AIMessage):
            result.append({"role": "assistant", "content": str(msg.content)})
    return result
