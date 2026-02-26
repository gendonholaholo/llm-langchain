"""Pydantic models for booking flow."""

from pydantic import BaseModel


class BookingParams(BaseModel):
    service_type: str | None = None
    preferred_date: str | None = None
    preferred_time: str | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    notes: str | None = None


class BookingRequest(BaseModel):
    service_type: str
    preferred_date: str
    preferred_time: str
    customer_name: str
    customer_phone: str
    notes: str = ""


class BookingResponse(BaseModel):
    success: bool
    reference_id: str | None = None
    message: str = ""
