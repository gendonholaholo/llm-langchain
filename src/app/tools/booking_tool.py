"""Booking tool for the agent."""

from langchain_core.tools import tool

from app.schemas.booking import BookingRequest, BookingResponse
from app.services.booking_api import BookingAPIClient


@tool
async def create_booking(
    service_type: str,
    preferred_date: str,
    preferred_time: str,
    customer_name: str,
    customer_phone: str,
    notes: str = "",
) -> str:
    """Create a booking for a customer. All fields are required except notes."""
    request = BookingRequest(
        service_type=service_type,
        preferred_date=preferred_date,
        preferred_time=preferred_time,
        customer_name=customer_name,
        customer_phone=customer_phone,
        notes=notes,
    )
    client = BookingAPIClient()
    try:
        result: BookingResponse = await client.create_booking(request)
        if result.success:
            return f"Booking confirmed! Reference ID: {result.reference_id}"
        return f"Booking failed: {result.message}"
    finally:
        await client.close()
