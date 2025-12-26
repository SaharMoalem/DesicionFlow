"""Tests for error handlers."""

import logging
from unittest.mock import patch

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import (
    AgentError,
    DecisionFlowError,
    LLMError,
    LLMRateLimitError,
    ValidationError,
)
from app.main import app
from app.schemas.errors import ErrorCode

client = TestClient(app)


def test_validation_exception_handler() -> None:
    """Test PydanticValidationError handler."""
    # Create a request that will trigger validation error
    invalid_data = {
        "decision_context": "Test",  # Too short (min_length=10)
        "options": ["Option 1"],  # Too few options (min_length=2)
    }

    with patch("app.api.middleware.error_handlers.logger") as mock_logger:
        response = client.post("/v1/decisions/analyze", json=invalid_data)

    # FastAPI returns 422 for validation errors, but our handler should transform it
    # However, FastAPI's automatic validation happens before our handler
    # So we expect 422 from FastAPI's default handler
    assert response.status_code == 422
    # Note: FastAPI's default validation error format is different from our ErrorResponse
    # In a real scenario, we'd need to override FastAPI's request validation


def test_request_id_middleware() -> None:
    """Test RequestIDMiddleware adds request_id to request state and response."""
    # Test with custom X-Request-ID header
    response = client.get(
        "/health", headers={"X-Request-ID": "custom-request-id"}
    )

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == "custom-request-id"

    # Test without header (should generate UUID)
    response = client.get("/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    request_id = response.headers.get("X-Request-ID")
    assert request_id is not None
    assert len(request_id) > 0


def test_agent_error_handler() -> None:
    """Test AgentError handler."""
    from app.api.v1.decisions import router

    @router.post("/test-agent-error")
    async def test_agent_error():
        raise AgentError("Agent failed", agent_name="clarifier")

    # Register test route
    app.include_router(router)

    with patch("app.api.middleware.error_handlers.logger") as mock_logger:
        response = client.post("/v1/decisions/test-agent-error")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.PIPELINE_ERROR.value
    assert data["error"]["details"]["agent"] == "clarifier"
    assert "request_id" in data

    # Verify logging was called with agent name
    mock_logger.error.assert_called_once()
    call_args = mock_logger.error.call_args
    assert call_args[1]["extra"]["agent_name"] == "clarifier"


def test_llm_error_handler() -> None:
    """Test LLMError handler."""
    from app.api.v1.decisions import router

    @router.post("/test-llm-error")
    async def test_llm_error():
        raise LLMError("LLM service unavailable", status_code=503)

    app.include_router(router)

    with patch("app.api.middleware.error_handlers.logger") as mock_logger:
        response = client.post("/v1/decisions/test-llm-error")

    assert response.status_code == 503
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.SERVICE_UNAVAILABLE.value
    assert "request_id" in data

    # Verify logging was called
    mock_logger.error.assert_called_once()


def test_llm_rate_limit_error_handler() -> None:
    """Test LLMRateLimitError handler."""
    from app.api.v1.decisions import router

    @router.post("/test-rate-limit-error")
    async def test_rate_limit_error():
        raise LLMRateLimitError("Rate limit exceeded")

    app.include_router(router)

    with patch("app.api.middleware.error_handlers.logger") as mock_logger:
        response = client.post("/v1/decisions/test-rate-limit-error")

    assert response.status_code == 429
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.RATE_LIMIT_EXCEEDED.value
    assert "request_id" in data

    # Verify logging was called
    mock_logger.error.assert_called_once()


def test_decision_flow_error_handler() -> None:
    """Test DecisionFlowError handler."""
    from app.api.v1.decisions import router

    @router.post("/test-decision-flow-error")
    async def test_decision_flow_error():
        raise DecisionFlowError("Pipeline execution failed")

    app.include_router(router)

    with patch("app.api.middleware.error_handlers.logger") as mock_logger:
        response = client.post("/v1/decisions/test-decision-flow-error")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.PIPELINE_ERROR.value
    assert "request_id" in data

    # Verify logging was called
    mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_generic_exception_handler() -> None:
    """Test generic exception handler for unhandled exceptions."""
    # Test the handler function directly
    from app.api.middleware.error_handlers import (
        generic_exception_handler,
        transform_exception_to_error_response,
    )

    # Test transform function
    error = ValueError("Unexpected error")
    error_response, status_code = transform_exception_to_error_response(
        error, "test-request-id"
    )

    assert status_code == 500
    assert error_response.error.code == ErrorCode.INTERNAL_ERROR
    assert error_response.request_id == "test-request-id"

    # Create a mock request with proper headers format
    from starlette.datastructures import Headers

    mock_request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/test",
            "headers": [("x-request-id", "test-request-id")],
        }
    )

    # Test handler with logging
    with patch("app.api.middleware.error_handlers.logger") as mock_logger:
        response = await generic_exception_handler(mock_request, error)

    assert response.status_code == 500
    import json

    data = json.loads(response.body.decode())
    assert "error" in data
    # Request ID should be present (either from header or generated)
    assert "request_id" in data
    assert data["request_id"] is not None

    # Verify logging was called with exc_info
    mock_logger.exception.assert_called_once()
    call_args = mock_logger.exception.call_args
    assert call_args[1]["exc_info"] is not None


def test_error_response_includes_request_id() -> None:
    """Test that all error responses include request_id."""
    # Test with a route that raises a handled exception
    from fastapi import APIRouter

    test_router = APIRouter()

    @test_router.post("/test-error-request-id")
    async def test_error_request_id():
        raise AgentError("Test error", agent_name="test_agent")

    app.include_router(test_router)

    response = client.post("/test-error-request-id")
    assert response.status_code == 500
    response_data = response.json()
    assert "error" in response_data
    assert "request_id" in response_data
    assert response_data["request_id"] is not None


def test_error_logging_includes_context() -> None:
    """Test that error logging includes full context."""
    from app.api.v1.decisions import router

    @router.post("/test-logging-context")
    async def test_logging_context():
        raise AgentError("Test error", agent_name="test_agent")

    app.include_router(router)

    with patch("app.api.middleware.error_handlers.logger") as mock_logger:
        response = client.post("/v1/decisions/test-logging-context")

    assert response.status_code == 500

    # Verify logging includes context
    mock_logger.error.assert_called_once()
    call_args = mock_logger.error.call_args
    extra = call_args[1]["extra"]
    assert "request_id" in extra
    assert "agent_name" in extra
    assert "error_type" in extra
    assert "error_message" in extra

