"""Tests for validation service."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from app.schemas.decision import DecisionRequest, DecisionResponse
from app.schemas.errors import ErrorCode
from app.validation.service import (
    ValidationResult,
    validate_agent_output,
    validate_request,
    validate_response,
)


@pytest.mark.asyncio
async def test_validate_request_valid() -> None:
    """Test validate_request with valid request data."""
    request_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
        "constraints": {"budget": 50000},
    }

    result = await validate_request(request_data)

    assert result.is_valid is True
    assert isinstance(result.data, DecisionRequest)
    assert result.data.decision_context == "Should we build feature X?"
    assert len(result.errors) == 0


@pytest.mark.asyncio
async def test_validate_request_invalid_missing_required() -> None:
    """Test validate_request with missing required fields."""
    request_data = {
        "decision_context": "Should we build feature X?",
        # Missing 'options' field
    }

    result = await validate_request(request_data, attempt_repair=False)

    assert result.is_valid is False
    assert len(result.errors) > 0
    assert any("options" in error.lower() for error in result.errors)


@pytest.mark.asyncio
async def test_validate_request_invalid_wrong_type() -> None:
    """Test validate_request with wrong type."""
    request_data = {
        "decision_context": "Should we build feature X?",
        "options": "not a list",  # Should be a list
    }

    result = await validate_request(request_data, attempt_repair=False)

    assert result.is_valid is False
    assert len(result.errors) > 0


@pytest.mark.asyncio
async def test_validate_request_repair_success() -> None:
    """Test validate_request with successful repair."""
    request_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now"],  # Only one option, needs 2+
    }

    # Mock repair to return fixed data
    repaired_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now", "Postpone"],  # Fixed: added second option
    }

    with patch("app.validation.service.repair_schema") as mock_repair:
        mock_repair.return_value = repaired_data

        result = await validate_request(request_data, attempt_repair=True)

        # Should succeed after repair
        assert result.is_valid is True
        assert isinstance(result.data, DecisionRequest)
        mock_repair.assert_called_once()


@pytest.mark.asyncio
async def test_validate_request_repair_failure() -> None:
    """Test validate_request with failed repair."""
    request_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now"],  # Only one option, needs 2+
    }

    # Mock repair to return still-invalid data
    repaired_data = {
        "decision_context": "Should we build feature X?",
        "options": ["Build now"],  # Still invalid
    }

    with patch("app.validation.service.repair_schema") as mock_repair:
        mock_repair.return_value = repaired_data

        result = await validate_request(request_data, attempt_repair=True)

        # Should fail after repair attempt
        assert result.is_valid is False
        assert len(result.errors) > 0
        mock_repair.assert_called_once()


@pytest.mark.asyncio
async def test_validate_agent_output_valid() -> None:
    """Test validate_agent_output with valid output."""
    from app.schemas.agents import ClarifierOutput

    output_data = {
        "missing_fields": [],
        "questions": [],
    }

    result = await validate_agent_output("clarifier", output_data)

    assert result.is_valid is True
    assert isinstance(result.data, ClarifierOutput)
    assert len(result.errors) == 0


@pytest.mark.asyncio
async def test_validate_agent_output_invalid() -> None:
    """Test validate_agent_output with invalid output."""
    output_data = {
        "missing_fields": "not a list",  # Should be a list
        "questions": [],
    }

    result = await validate_agent_output("clarifier", output_data, attempt_repair=False)

    assert result.is_valid is False
    assert len(result.errors) > 0


@pytest.mark.asyncio
async def test_validate_agent_output_unknown_agent() -> None:
    """Test validate_agent_output with unknown agent name."""
    output_data = {"test": "data"}

    result = await validate_agent_output("unknown_agent", output_data)

    assert result.is_valid is False
    assert len(result.errors) > 0
    assert "Unknown agent name" in result.errors[0]


@pytest.mark.asyncio
async def test_validate_agent_output_repair_success() -> None:
    """Test validate_agent_output with successful repair."""
    output_data = {
        "missing_fields": "not a list",  # Invalid type
        "questions": [],
    }

    # Mock repair to return fixed data
    repaired_data = {
        "missing_fields": [],  # Fixed: converted to list
        "questions": [],
    }

    with patch("app.validation.service.repair_schema") as mock_repair:
        mock_repair.return_value = repaired_data

        result = await validate_agent_output("clarifier", output_data, attempt_repair=True)

        # Should succeed after repair
        assert result.is_valid is True
        mock_repair.assert_called_once()


@pytest.mark.asyncio
async def test_validate_response_valid() -> None:
    """Test validate_response with valid response."""
    from app.schemas.decision import ConfidenceBreakdown, Criterion, OptionScores
    from app.schemas.versioning import VersionMetadata

    response_data = {
        "decision": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
        "criteria": [
            {"name": "cost", "weight": 0.5, "rationale": "Cost matters"},
        ],
        "scores": {
            "Build now": {
                "total_score": 0.75,
                "breakdown": [],
            },
        },
        "winner": "Build now",
        "confidence": 0.78,
        "confidence_breakdown": {
            "input_completeness": 0.8,
            "agent_agreement": 0.9,
            "evidence_strength": 0.75,
            "bias_impact": 0.85,
        },
        "biases_detected": [],
        "trade_offs": [],
        "assumptions": [],
        "risks": [],
        "what_would_change_decision": [],
        "meta": {
            "api_version": "v1",
            "logic_version": "1.0.0",
            "schema_version": "1.0.0",
        },
        "request_id": "test_req",
    }

    result = await validate_response(response_data)

    assert result.is_valid is True
    assert isinstance(result.data, DecisionResponse)
    assert len(result.errors) == 0


@pytest.mark.asyncio
async def test_validate_response_invalid() -> None:
    """Test validate_response with invalid response."""
    response_data = {
        "decision": "Should we build feature X?",
        # Missing required fields
    }

    result = await validate_response(response_data, attempt_repair=False)

    assert result.is_valid is False
    assert len(result.errors) > 0


@pytest.mark.asyncio
async def test_validate_response_repair_success() -> None:
    """Test validate_response with successful repair."""
    response_data = {
        "decision": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
        # Missing other required fields
    }

    # Mock repair to return fixed data
    repaired_data = {
        "decision": "Should we build feature X?",
        "options": ["Build now", "Postpone"],
        "criteria": [],
        "scores": {},
        "winner": "Build now",
        "confidence": 0.8,
        "confidence_breakdown": {
            "input_completeness": 0.8,
            "agent_agreement": 0.8,
            "evidence_strength": 0.8,
            "bias_impact": 0.8,
        },
        "biases_detected": [],
        "trade_offs": [],
        "assumptions": [],
        "risks": [],
        "what_would_change_decision": [],
        "meta": {
            "api_version": "v1",
            "logic_version": "1.0.0",
            "schema_version": "1.0.0",
        },
        "request_id": "test_req",
    }

    with patch("app.validation.service.repair_schema") as mock_repair:
        mock_repair.return_value = repaired_data

        result = await validate_response(response_data, attempt_repair=True)

        # Should succeed after repair
        assert result.is_valid is True
        assert isinstance(result.data, DecisionResponse)
        mock_repair.assert_called_once()
