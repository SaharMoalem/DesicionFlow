"""Tests for PipelineState schema."""

import pytest
from pydantic import ValidationError

from app.schemas.state import PipelineState


def test_pipeline_state_valid() -> None:
    """Test PipelineState with valid data."""
    state = PipelineState(
        request_id="req_123",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Should we build feature X?",
            "options": ["Build now", "Postpone"],
        },
    )
    assert state.request_id == "req_123"
    assert state.api_version == "v1"
    assert state.logic_version == "1.0.0"
    assert state.schema_version == "1.0.0"
    assert state.normalized_input is not None
    assert state.clarifier_output is None
    assert state.derived_artifacts == {}


def test_pipeline_state_with_agent_outputs() -> None:
    """Test PipelineState with agent outputs."""
    state = PipelineState(
        request_id="req_123",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={"decision_context": "Test", "options": ["opt1", "opt2"]},
        clarifier_output={"missing_fields": [], "questions": []},
        criteria_builder_output={"criteria": [{"name": "cost", "weight": 0.5}]},
        derived_artifacts={"criteria": [{"name": "cost", "weight": 0.5}]},
    )
    assert state.clarifier_output is not None
    assert state.criteria_builder_output is not None
    assert len(state.derived_artifacts) > 0


def test_pipeline_state_extra_fields_forbidden() -> None:
    """Test PipelineState rejects extra fields."""
    with pytest.raises(ValidationError) as exc_info:
        PipelineState(
            request_id="req_123",
            api_version="v1",
            logic_version="1.0.0",
            schema_version="1.0.0",
            normalized_input={},
            extra_field="not allowed",
        )
    assert "extra" in str(exc_info.value).lower() and "not permitted" in str(
        exc_info.value
    ).lower()


def test_pipeline_state_required_fields() -> None:
    """Test PipelineState requires all mandatory fields."""
    with pytest.raises(ValidationError):
        PipelineState(
            request_id="req_123",
            # Missing api_version, logic_version, schema_version, normalized_input
        )

