"""Tests for error schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.errors import ErrorCode, ErrorDetail, ErrorResponse


def test_error_code_enum() -> None:
    """Test ErrorCode enum values."""
    assert ErrorCode.INVALID_REQUEST == "INVALID_REQUEST"
    assert ErrorCode.SCHEMA_VALIDATION_FAILED == "SCHEMA_VALIDATION_FAILED"
    assert ErrorCode.RATE_LIMIT_EXCEEDED == "RATE_LIMIT_EXCEEDED"
    assert ErrorCode.UNAUTHORIZED == "UNAUTHORIZED"


def test_error_detail_valid() -> None:
    """Test ErrorDetail with valid data."""
    error = ErrorDetail(
        code=ErrorCode.INVALID_REQUEST,
        message="Request payload fails schema validation",
        details={"field": "options", "issue": "missing required field"},
    )
    assert error.code == ErrorCode.INVALID_REQUEST
    assert error.message is not None
    assert error.details is not None


def test_error_detail_without_details() -> None:
    """Test ErrorDetail without optional details."""
    error = ErrorDetail(
        code=ErrorCode.INTERNAL_ERROR,
        message="An unexpected error occurred",
    )
    assert error.code == ErrorCode.INTERNAL_ERROR
    assert error.details is None


def test_error_detail_extra_fields_forbidden() -> None:
    """Test ErrorDetail rejects extra fields."""
    with pytest.raises(ValidationError) as exc_info:
        ErrorDetail(
            code=ErrorCode.INVALID_REQUEST,
            message="Test",
            extra_field="not allowed",
        )
    assert "extra" in str(exc_info.value).lower() and "not permitted" in str(
        exc_info.value
    ).lower()


def test_error_response_valid() -> None:
    """Test ErrorResponse with valid data."""
    response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.SCHEMA_VALIDATION_FAILED,
            message="Agent output failed schema validation",
            details={"agent": "clarifier", "validation_errors": []},
        ),
        request_id="req_123",
    )
    assert response.error.code == ErrorCode.SCHEMA_VALIDATION_FAILED
    assert response.request_id == "req_123"
    assert response.error.details is not None


def test_error_response_extra_fields_forbidden() -> None:
    """Test ErrorResponse rejects extra fields."""
    with pytest.raises(ValidationError) as exc_info:
        ErrorResponse(
            error=ErrorDetail(
                code=ErrorCode.INVALID_REQUEST,
                message="Test",
            ),
            request_id="req_123",
            extra_field="not allowed",
        )
    assert "extra" in str(exc_info.value).lower() and "not permitted" in str(
        exc_info.value
    ).lower()

