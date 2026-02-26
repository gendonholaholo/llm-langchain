"""LangGraph agent state definition."""

from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.constants import BookingStep, Intent


class GuardrailResult(TypedDict):
    passed: bool
    blocked_reason: str | None


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    phone_number: str
    conversation_id: int
    detected_language: str
    intent: Intent
    guardrail_result: GuardrailResult
    booking_params: dict
    booking_step: BookingStep
    retrieved_docs: list[str]
