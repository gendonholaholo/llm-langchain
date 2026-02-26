"""Health check endpoint."""

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import async_session_factory
from app.services.waha_client import WahaClient

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Check DB and WAHA connectivity."""
    status: dict[str, str | bool] = {"status": "ok"}

    # Check DB
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        status["database"] = "connected"
    except Exception:
        status["database"] = "disconnected"
        status["status"] = "degraded"

    # Check WAHA
    waha = WahaClient()
    try:
        waha_ok = await waha.check_health()
        status["waha"] = "connected" if waha_ok else "disconnected"
        if not waha_ok:
            status["status"] = "degraded"
    except Exception:
        status["waha"] = "disconnected"
        status["status"] = "degraded"
    finally:
        await waha.close()

    return status
