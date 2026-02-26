"""API router aggregation."""

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.webhook import router as webhook_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(webhook_router, tags=["webhook"])
