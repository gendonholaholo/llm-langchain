"""LangGraph graph builder for the WhatsApp agent."""

from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    blocked_response_node,
    booking_check_route,
    booking_node,
    general_respond_node,
    guardrails_node,
    rag_node,
    rag_respond_node,
    router_node,
    submit_booking_node,
)
from app.agent.state import AgentState
from app.constants import Intent


def _guardrail_route(state: AgentState) -> str:
    if state["guardrail_result"]["passed"]:
        return "router"
    return "blocked"


def _intent_route(state: AgentState) -> str:
    intent = state["intent"]
    if intent in (Intent.FAQ, Intent.PRODUCT_INQUIRY):
        return "rag"
    if intent == Intent.BOOKING:
        return "booking"
    return "general"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("guardrails", guardrails_node)
    graph.add_node("router", router_node)
    graph.add_node("blocked_response", blocked_response_node)
    graph.add_node("general_respond", general_respond_node)
    graph.add_node("rag", rag_node)
    graph.add_node("rag_respond", rag_respond_node)
    graph.add_node("booking", booking_node)
    graph.add_node("submit_booking", submit_booking_node)

    # Entry point
    graph.set_entry_point("guardrails")

    # Guardrails → router or blocked
    graph.add_conditional_edges(
        "guardrails",
        _guardrail_route,
        {"router": "router", "blocked": "blocked_response"},
    )

    # Blocked → END
    graph.add_edge("blocked_response", END)

    # Router → intent-based routing
    graph.add_conditional_edges(
        "router",
        _intent_route,
        {"rag": "rag", "booking": "booking", "general": "general_respond"},
    )

    # General → END
    graph.add_edge("general_respond", END)

    # RAG flow
    graph.add_edge("rag", "rag_respond")
    graph.add_edge("rag_respond", END)

    # Booking flow
    graph.add_conditional_edges(
        "booking",
        booking_check_route,
        {"submit": "submit_booking", "continue": END, "done": END},
    )
    graph.add_edge("submit_booking", END)

    return graph


# Compiled graph singleton
agent_graph = build_graph().compile()
