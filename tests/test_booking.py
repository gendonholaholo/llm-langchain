"""Tests for booking schemas and flow."""

from app.constants import BookingStep
from app.schemas.booking import BookingParams, BookingRequest, BookingResponse


class TestBookingParams:
    def test_empty_params(self):
        params = BookingParams()
        assert params.service_type is None
        assert params.preferred_date is None
        assert params.preferred_time is None
        assert params.customer_name is None

    def test_partial_params(self):
        params = BookingParams(service_type="haircut", preferred_date="2026-03-01")
        assert params.service_type == "haircut"
        assert params.preferred_date == "2026-03-01"
        assert params.preferred_time is None

    def test_full_params(self):
        params = BookingParams(
            service_type="haircut",
            preferred_date="2026-03-01",
            preferred_time="14:00",
            customer_name="John",
            customer_phone="6281234567890",
        )
        assert params.customer_name == "John"


class TestBookingRequest:
    def test_valid_request(self):
        req = BookingRequest(
            service_type="haircut",
            preferred_date="2026-03-01",
            preferred_time="14:00",
            customer_name="John",
            customer_phone="6281234567890",
        )
        assert req.notes == ""

    def test_request_serialization(self):
        req = BookingRequest(
            service_type="haircut",
            preferred_date="2026-03-01",
            preferred_time="14:00",
            customer_name="John",
            customer_phone="6281234567890",
            notes="No preference",
        )
        data = req.model_dump()
        assert data["service_type"] == "haircut"
        assert data["notes"] == "No preference"


class TestBookingResponse:
    def test_success_response(self):
        resp = BookingResponse(success=True, reference_id="BK-001", message="Booking confirmed")
        assert resp.success is True
        assert resp.reference_id == "BK-001"

    def test_failure_response(self):
        resp = BookingResponse(success=False, message="Time slot unavailable")
        assert resp.success is False
        assert resp.reference_id is None


class TestBookingStepEnum:
    def test_step_values(self):
        assert BookingStep.IDLE == "idle"
        assert BookingStep.COLLECTING_SERVICE == "collecting_service"
        assert BookingStep.COMPLETED == "completed"
