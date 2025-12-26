"""Tests for decision analysis API endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import AgentError, DecisionFlowError, LLMError, ValidationError
from app.main import app
from app.schemas.decision import DecisionRequest, DecisionResponse
from app.schemas.errors import ErrorCode
from app.schemas.versioning import VersionMetadata

client = TestClient(app)


@pytest.mark.asyncio
async def test_analyze_decision_successful_flow() -> None:
    """Test successful decision analysis flow."""
    request_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
        "constraints": {"budget": 50000},
    }

    # Mock pipeline to return successful response
    mock_response = DecisionResponse(
        decision="Should we build feature X?",
        options=["Build now", "Postpone"],
        criteria=[],
        scores={},
        winner="Build now",
        confidence=0.78,
        confidence_breakdown={
            "input_completeness": 0.8,
            "agent_agreement": 0.9,
            "evidence_strength": 0.75,
            "bias_impact": 0.85,
        },
        biases_detected=[],
        trade_offs=[],
        assumptions=[],
        risks=[],
        what_would_change_decision=[],
        meta=VersionMetadata(
            api_version="v1",
            logic_version="1.0.0",
            schema_version="1.0.0",
        ),
        request_id="test_req",
    )

    with patch("app.api.v1.decisions.run_pipeline") as mock_run_pipeline, patch(
        "app.api.v1.decisions.validate_request"
    ) as mock_validate_request, patch(
        "app.api.v1.decisions.validate_response"
    ) as mock_validate_response:
        mock_validate_request.return_value = type(
            "ValidationResult", (), {"is_valid": True, "data": None, "errors": []}
        )()
        mock_validate_response.return_value = type(
            "ValidationResult", (), {"is_valid": True, "data": None, "errors": []}
        )()
        mock_run_pipeline.return_value = mock_response

        response = client.post("/v1/decisions/analyze", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["winner"] == "Build now"
    assert data["confidence"] == 0.78
    assert "request_id" in data
    assert data["request_id"] is not None
    assert "meta" in data
    assert data["meta"]["api_version"] == "v1"
    assert data["meta"]["logic_version"] == "1.0.0"
    assert data["meta"]["schema_version"] == "1.0.0"


@pytest.mark.asyncio
async def test_analyze_decision_generates_request_id() -> None:
    """Test endpoint generates request_id at entry point."""
    request_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
    }

    mock_response = DecisionResponse(
        decision="Test",
        options=["Build now", "Postpone"],
        criteria=[],
        scores={},
        winner="Build now",
        confidence=0.8,
        confidence_breakdown={
            "input_completeness": 0.8,
            "agent_agreement": 0.8,
            "evidence_strength": 0.8,
            "bias_impact": 0.8,
        },
        biases_detected=[],
        trade_offs=[],
        assumptions=[],
        risks=[],
        what_would_change_decision=[],
        meta=VersionMetadata(
            api_version="v1",
            logic_version="1.0.0",
            schema_version="1.0.0",
        ),
        request_id="generated_id",
    )

    with patch("app.api.v1.decisions.run_pipeline") as mock_run_pipeline, patch(
        "app.api.v1.decisions.validate_request"
    ) as mock_validate_request, patch(
        "app.api.v1.decisions.validate_response"
    ) as mock_validate_response:
        mock_validate_request.return_value = type(
            "ValidationResult", (), {"is_valid": True, "data": None, "errors": []}
        )()
        mock_validate_response.return_value = type(
            "ValidationResult", (), {"is_valid": True, "data": None, "errors": []}
        )()
        mock_run_pipeline.return_value = mock_response

        response = client.post("/v1/decisions/analyze", json=request_data)

    assert response.status_code == 200
    data = response.json()
    # Verify request_id was generated and passed to pipeline
    assert "request_id" in data
    call_args = mock_run_pipeline.call_args
    assert call_args[1]["request_id"] is not None


@pytest.mark.asyncio
async def test_analyze_decision_validation_error() -> None:
    """Test endpoint handles validation errors correctly."""
    # Test FastAPI's automatic validation (missing required field)
    request_data = {
        "decision_context": "Should we build feature X?",
        # Missing required 'options' field
    }

    response = client.post("/v1/decisions/analyze", json=request_data)

    # FastAPI returns 422 for validation errors before reaching our handler
    assert response.status_code == 422

    # Test our custom validation (after FastAPI validation passes)
    request_data_valid = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
    }

    with patch("app.api.v1.decisions.validate_request") as mock_validate_request:
        mock_validate_request.return_value = type(
            "ValidationResult",
            (),
            {"is_valid": False, "data": None, "errors": ["Custom validation failed"]},
        )()

        response = client.post("/v1/decisions/analyze", json=request_data_valid)

    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.INVALID_REQUEST.value
    assert "request_id" in data
    assert data["request_id"] is not None


@pytest.mark.asyncio
async def test_analyze_decision_pipeline_error() -> None:
    """Test endpoint handles pipeline errors correctly."""
    request_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
    }

    with patch("app.api.v1.decisions.run_pipeline") as mock_run_pipeline, patch(
        "app.api.v1.decisions.validate_request"
    ) as mock_validate_request:
        mock_validate_request.return_value = type(
            "ValidationResult", (), {"is_valid": True, "data": None, "errors": []}
        )()
        mock_run_pipeline.side_effect = DecisionFlowError("Pipeline execution failed")

        response = client.post("/v1/decisions/analyze", json=request_data)

    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.PIPELINE_ERROR.value
    assert "request_id" in data
    assert data["request_id"] is not None


@pytest.mark.asyncio
async def test_analyze_decision_agent_error() -> None:
    """Test endpoint handles agent errors correctly."""
    request_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
    }

    with patch("app.api.v1.decisions.run_pipeline") as mock_run_pipeline, patch(
        "app.api.v1.decisions.validate_request"
    ) as mock_validate_request:
        mock_validate_request.return_value = type(
            "ValidationResult", (), {"is_valid": True, "data": None, "errors": []}
        )()
        mock_run_pipeline.side_effect = AgentError("Agent failed", agent_name="clarifier")

        response = client.post("/v1/decisions/analyze", json=request_data)

    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.PIPELINE_ERROR.value
    assert "request_id" in data


@pytest.mark.asyncio
async def test_analyze_decision_llm_error() -> None:
    """Test endpoint handles LLM errors correctly."""
    request_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
    }

    with patch("app.api.v1.decisions.run_pipeline") as mock_run_pipeline, patch(
        "app.api.v1.decisions.validate_request"
    ) as mock_validate_request:
        mock_validate_request.return_value = type(
            "ValidationResult", (), {"is_valid": True, "data": None, "errors": []}
        )()
        mock_run_pipeline.side_effect = LLMError("LLM service unavailable", status_code=503)

        response = client.post("/v1/decisions/analyze", json=request_data)

    assert response.status_code == 503
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.SERVICE_UNAVAILABLE.value
    assert "request_id" in data


@pytest.mark.asyncio
async def test_analyze_decision_llm_rate_limit_error() -> None:
    """Test endpoint handles LLM rate limit errors correctly."""
    request_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
    }

    with patch("app.api.v1.decisions.run_pipeline") as mock_run_pipeline, patch(
        "app.api.v1.decisions.validate_request"
    ) as mock_validate_request:
        mock_validate_request.return_value = type(
            "ValidationResult", (), {"is_valid": True, "data": None, "errors": []}
        )()
        from app.core.exceptions import LLMRateLimitError

        mock_run_pipeline.side_effect = LLMRateLimitError("Rate limit exceeded")

        response = client.post("/v1/decisions/analyze", json=request_data)

    assert response.status_code == 429
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.RATE_LIMIT_EXCEEDED.value
    assert "request_id" in data


@pytest.mark.asyncio
async def test_analyze_decision_response_validation_error() -> None:
    """Test endpoint validates response payload before returning."""
    request_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
    }

    mock_response = DecisionResponse(
        decision="Test",
        options=["Build now", "Postpone"],
        criteria=[],
        scores={},
        winner="Build now",
        confidence=0.8,
        confidence_breakdown={
            "input_completeness": 0.8,
            "agent_agreement": 0.8,
            "evidence_strength": 0.8,
            "bias_impact": 0.8,
        },
        biases_detected=[],
        trade_offs=[],
        assumptions=[],
        risks=[],
        what_would_change_decision=[],
        meta=VersionMetadata(
            api_version="v1",
            logic_version="1.0.0",
            schema_version="1.0.0",
        ),
        request_id="test_req",
    )

    with patch("app.api.v1.decisions.run_pipeline") as mock_run_pipeline, patch(
        "app.api.v1.decisions.validate_request"
    ) as mock_validate_request, patch(
        "app.api.v1.decisions.validate_response"
    ) as mock_validate_response:
        mock_validate_request.return_value = type(
            "ValidationResult", (), {"is_valid": True, "data": None, "errors": []}
        )()
        mock_validate_response.return_value = type(
            "ValidationResult",
            (),
            {"is_valid": False, "data": None, "errors": ["Response validation failed"]},
        )()
        mock_run_pipeline.return_value = mock_response

        response = client.post("/v1/decisions/analyze", json=request_data)

    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.INVALID_REQUEST.value
    assert "request_id" in data


@pytest.mark.asyncio
async def test_analyze_decision_includes_version_metadata() -> None:
    """Test endpoint includes version metadata in response."""
    request_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
    }

    mock_response = DecisionResponse(
        decision="Should we build feature X?",
        options=["Build now", "Postpone"],
        criteria=[],
        scores={},
        winner="Build now",
        confidence=0.78,
        confidence_breakdown={
            "input_completeness": 0.8,
            "agent_agreement": 0.9,
            "evidence_strength": 0.75,
            "bias_impact": 0.85,
        },
        biases_detected=[],
        trade_offs=[],
        assumptions=[],
        risks=[],
        what_would_change_decision=[],
        meta=VersionMetadata(
            api_version="v1",
            logic_version="1.0.0",
            schema_version="1.0.0",
        ),
        request_id="test_req",
    )

    with patch("app.api.v1.decisions.run_pipeline") as mock_run_pipeline, patch(
        "app.api.v1.decisions.validate_request"
    ) as mock_validate_request, patch(
        "app.api.v1.decisions.validate_response"
    ) as mock_validate_response:
        mock_validate_request.return_value = type(
            "ValidationResult", (), {"is_valid": True, "data": None, "errors": []}
        )()
        mock_validate_response.return_value = type(
            "ValidationResult", (), {"is_valid": True, "data": None, "errors": []}
        )()
        mock_run_pipeline.return_value = mock_response

        response = client.post("/v1/decisions/analyze", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert data["meta"]["api_version"] == "v1"
    assert data["meta"]["logic_version"] == "1.0.0"
    assert data["meta"]["schema_version"] == "1.0.0"

