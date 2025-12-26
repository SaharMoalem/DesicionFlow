"""Tests for JSON Schema definitions."""

import pytest

from app.schemas.decision import DecisionRequest, DecisionResponse
from app.schemas.errors import ErrorCode
from app.validation.schemas import (
    get_json_schema,
    get_json_schema_for_agent_output,
    get_json_schema_for_request,
    get_json_schema_for_response,
)


def test_get_json_schema() -> None:
    """Test get_json_schema returns valid JSON Schema."""
    schema = get_json_schema(DecisionRequest)

    assert isinstance(schema, dict)
    assert "type" in schema or "properties" in schema
    assert "properties" in schema or "$defs" in schema


def test_get_json_schema_for_request() -> None:
    """Test get_json_schema_for_request returns DecisionRequest schema."""
    schema = get_json_schema_for_request()

    assert isinstance(schema, dict)
    # Verify it contains DecisionRequest fields
    assert "properties" in schema
    assert "decision_context" in schema["properties"]
    assert "options" in schema["properties"]


def test_get_json_schema_for_response() -> None:
    """Test get_json_schema_for_response returns DecisionResponse schema."""
    schema = get_json_schema_for_response()

    assert isinstance(schema, dict)
    # Verify it contains DecisionResponse fields
    assert "properties" in schema
    assert "decision" in schema["properties"]
    assert "winner" in schema["properties"]


def test_get_json_schema_for_agent_output_clarifier() -> None:
    """Test get_json_schema_for_agent_output for clarifier."""
    schema = get_json_schema_for_agent_output("clarifier")

    assert isinstance(schema, dict)
    assert "properties" in schema
    assert "missing_fields" in schema["properties"]
    assert "questions" in schema["properties"]


def test_get_json_schema_for_agent_output_criteria_builder() -> None:
    """Test get_json_schema_for_agent_output for criteria_builder."""
    schema = get_json_schema_for_agent_output("criteria_builder")

    assert isinstance(schema, dict)
    assert "properties" in schema
    assert "criteria" in schema["properties"]


def test_get_json_schema_for_agent_output_bias_checker() -> None:
    """Test get_json_schema_for_agent_output for bias_checker."""
    schema = get_json_schema_for_agent_output("bias_checker")

    assert isinstance(schema, dict)
    assert "properties" in schema
    assert "bias_findings" in schema["properties"]


def test_get_json_schema_for_agent_output_option_evaluator() -> None:
    """Test get_json_schema_for_agent_output for option_evaluator."""
    schema = get_json_schema_for_agent_output("option_evaluator")

    assert isinstance(schema, dict)
    assert "properties" in schema
    assert "scores" in schema["properties"]


def test_get_json_schema_for_agent_output_decision_synthesizer() -> None:
    """Test get_json_schema_for_agent_output for decision_synthesizer."""
    schema = get_json_schema_for_agent_output("decision_synthesizer")

    assert isinstance(schema, dict)
    assert "properties" in schema
    assert "winner" in schema["properties"]
    assert "confidence" in schema["properties"]


def test_get_json_schema_for_agent_output_unknown_agent() -> None:
    """Test get_json_schema_for_agent_output raises ValueError for unknown agent."""
    with pytest.raises(ValueError) as exc_info:
        get_json_schema_for_agent_output("unknown_agent")

    assert "Unknown agent name" in str(exc_info.value)

