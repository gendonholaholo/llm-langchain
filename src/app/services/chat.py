"""Chat service: orchestrates webhook → agent → reply."""

from datetime import UTC, datetime, timedelta

import structlog
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy import select

from app.agent.graph import agent_graph
from app.agent.state import AgentState
from app.constants import (
    CONVERSATION_TIMEOUT_HOURS,
    MAX_HISTORY_MESSAGES,
    MAX_MESSAGE_LENGTH,
    BookingStep,
    Intent,
    Role,
)
from app.core.database import async_session_factory
from app.models.db import Conversation, Message
from app.services.waha_client import WahaClient

logger = structlog.get_logger(__name__)


class ChatService:
    @staticmethod
    async def process_message(phone_number: str, chat_id: str, message_body: str) -> None:
        """Process an incoming message end-to-end."""
        waha = WahaClient()
        try:
            await waha.send_seen(chat_id)

            # Truncate overly long messages
            if len(message_body) > MAX_MESSAGE_LENGTH:
                message_body = message_body[:MAX_MESSAGE_LENGTH]

            async with async_session_factory() as session:
                # Get or create conversation
                conversation = await ChatService._get_or_create_conversation(
                    session, phone_number
                )

                # Save user message
                user_msg = Message(
                    conversation_id=conversation.id,
                    role=Role.USER,
                    content=message_body,
                )
                session.add(user_msg)
                await session.flush()

                # Load history
                history = await ChatService._load_history(session, conversation.id)

                # Build agent state
                booking_meta = (conversation.metadata_ or {}).get("booking", {})
                initial_state: AgentState = {
                    "messages": history,
                    "phone_number": phone_number,
                    "conversation_id": conversation.id,
                    "detected_language": (conversation.metadata_ or {}).get(
                        "language", "Indonesian"
                    ),
                    "intent": Intent.GENERAL,
                    "guardrail_result": {"passed": True, "blocked_reason": None},
                    "booking_params": booking_meta.get("params", {}),
                    "booking_step": BookingStep(
                        booking_meta.get("step", BookingStep.IDLE)
                    ),
                    "retrieved_docs": [],
                }

                # Invoke the agent graph
                result = await agent_graph.ainvoke(initial_state)

                # Extract assistant reply
                reply_text = ""
                if result["messages"]:
                    last_msg = result["messages"][-1]
                    if isinstance(last_msg, AIMessage):
                        reply_text = str(last_msg.content)

                if not reply_text:
                    reply_text = "Sorry, I couldn't process your message. Please try again."

                # Save assistant message
                assistant_msg = Message(
                    conversation_id=conversation.id,
                    role=Role.ASSISTANT,
                    content=reply_text,
                    intent=result.get("intent"),
                )
                session.add(assistant_msg)

                # Update conversation metadata with booking state
                meta = conversation.metadata_ or {}
                meta["booking"] = {
                    "params": result.get("booking_params", {}),
                    "step": result.get("booking_step", BookingStep.IDLE),
                }
                meta["language"] = result.get("detected_language", "Indonesian")
                conversation.metadata_ = meta
                conversation.last_active_at = datetime.now(UTC)

                await session.commit()

            # Send reply via WAHA
            await waha.send_text(chat_id, reply_text)
            logger.info(
                "chat.reply_sent",
                phone_number=phone_number,
                intent=result.get("intent"),
                reply_length=len(reply_text),
            )

        except Exception:
            logger.exception("chat.process_failed", phone_number=phone_number)
            try:
                await waha.send_text(
                    chat_id,
                    "Sorry, an error occurred. Please try again later.",
                )
            except Exception:
                logger.exception("chat.error_reply_failed")
        finally:
            await waha.close()

    @staticmethod
    async def _get_or_create_conversation(
        session, phone_number: str  # noqa: ANN001
    ) -> Conversation:
        """Get active conversation or create a new one."""
        timeout = datetime.now(UTC) - timedelta(hours=CONVERSATION_TIMEOUT_HOURS)
        stmt = (
            select(Conversation)
            .where(Conversation.phone_number == phone_number)
            .where(Conversation.last_active_at >= timeout)
            .order_by(Conversation.last_active_at.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        conversation = result.scalar_one_or_none()

        if conversation is None:
            conversation = Conversation(phone_number=phone_number, metadata_={})
            session.add(conversation)
            await session.flush()

        return conversation

    @staticmethod
    async def _load_history(
        session, conversation_id: int  # noqa: ANN001
    ) -> list[HumanMessage | AIMessage]:
        """Load recent messages as LangChain message objects."""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(MAX_HISTORY_MESSAGES)
        )
        result = await session.execute(stmt)
        db_messages = list(reversed(result.scalars().all()))

        history: list[HumanMessage | AIMessage] = []
        for msg in db_messages:
            if msg.role == Role.USER:
                history.append(HumanMessage(content=msg.content))
            elif msg.role == Role.ASSISTANT:
                history.append(AIMessage(content=msg.content))

        return history
