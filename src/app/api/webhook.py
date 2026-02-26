"""WAHA webhook endpoint."""

import structlog
from fastapi import APIRouter, BackgroundTasks, Response

from app.constants import WahaEventType
from app.schemas.waha import WahaWebhookPayload
from app.services.chat import ChatService

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/webhook/waha")
async def waha_webhook(
    payload: WahaWebhookPayload,
    background_tasks: BackgroundTasks,
) -> Response:
    """Receive WAHA webhook events and process messages in the background."""
    if payload.event != WahaEventType.MESSAGE:
        return Response(status_code=200)

    if payload.is_from_me():
        return Response(status_code=200)

    body = payload.get_message_body()
    phone_number = payload.extract_phone_number()

    if not body or not phone_number:
        logger.warning("webhook.invalid_payload", waha_event=payload.event)
        return Response(status_code=200)

    chat_id = payload.get_chat_id()
    if not chat_id:
        return Response(status_code=200)

    logger.info("webhook.received", phone_number=phone_number, body_length=len(body))

    background_tasks.add_task(
        ChatService.process_message,
        phone_number=phone_number,
        chat_id=chat_id,
        message_body=body,
    )

    return Response(status_code=200)
