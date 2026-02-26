"""Tests for the LangGraph agent."""

from app.agent.state import AgentState
from app.constants import BookingStep, Intent


class TestAgentState:
    def test_agent_state_defaults(self):
        """AgentState should accept all required fields."""
        state: AgentState = {
            "messages": [],
            "phone_number": "6281234567890",
            "conversation_id": 1,
            "detected_language": "Indonesian",
            "intent": Intent.GENERAL,
            "guardrail_result": {"passed": True, "blocked_reason": None},
            "booking_params": {},
            "booking_step": BookingStep.IDLE,
            "retrieved_docs": [],
        }
        assert state["phone_number"] == "6281234567890"
        assert state["intent"] == Intent.GENERAL
        assert state["guardrail_result"]["passed"] is True

    def test_intent_enum_values(self):
        """All intent values should be valid."""
        assert Intent.GREETING == "greeting"
        assert Intent.FAQ == "faq"
        assert Intent.PRODUCT_INQUIRY == "product_inquiry"
        assert Intent.BOOKING == "booking"
        assert Intent.GENERAL == "general"
        assert Intent.OFF_TOPIC == "off_topic"
        assert Intent.BLOCKED == "blocked"

    def test_booking_step_flow(self):
        """BookingStep should have all required steps."""
        steps = [
            BookingStep.IDLE,
            BookingStep.COLLECTING_SERVICE,
            BookingStep.COLLECTING_DATE,
            BookingStep.COLLECTING_TIME,
            BookingStep.COLLECTING_NAME,
            BookingStep.CONFIRMING,
            BookingStep.SUBMITTING,
            BookingStep.COMPLETED,
        ]
        assert len(steps) == 8
