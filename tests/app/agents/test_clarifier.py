"""Tests for Clarifier Agent."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.clarifier import Clarifier
from app.core.exceptions import AgentError, ValidationError
from app.schemas.agents import ClarifierInput, ClarifierOutput
from app.schemas.state import PipelineState


@pytest.fixture
def clarifier() -> Clarifier:
    """Create Clarifier agent instance."""
    return Clarifier()


def test_clarifier_name(clarifier: Clarifier) -> None:
    """Test Clarifier agent name."""
    assert clarifier.name == "clarifier"


@pytest.mark.asyncio
async def test_clarifier_execute_identifies_missing_inputs(clarifier: Clarifier) -> None:
    """Test Clarifier identifies missing inputs correctly."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Should we build feature X?",
            "options": ["Build now", "Postpone"],
            # Missing constraints, criteria_preferences
        },
    )

    # Mock LLM response
    mock_response = json.dumps({
        "missing_fields": ["budget", "timeline"],
        "questions": [
            "What is the budget constraint?",
            "What is the required timeline?",
        ],
    })

    with patch("app.agents.clarifier.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await clarifier.execute(state)

    assert isinstance(result, ClarifierOutput)
    assert len(result.missing_fields) == 2
    assert "budget" in result.missing_fields
    assert "timeline" in result.missing_fields
    assert len(result.questions) == 2


@pytest.mark.asyncio
async def test_clarifier_execute_all_inputs_present(clarifier: Clarifier) -> None:
    """Test Clarifier returns empty lists when all inputs are present."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Should we build feature X? We have a budget of $50k and need to deliver in Q2.",
            "options": ["Build now", "Postpone"],
            "constraints": {"budget": 50000, "timeline": "Q2"},
            "criteria_preferences": ["time_to_market", "cost"],
        },
    )

    # Mock LLM response indicating all inputs present
    mock_response = json.dumps({
        "missing_fields": [],
        "questions": [],
    })

    with patch("app.agents.clarifier.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await clarifier.execute(state)

    assert isinstance(result, ClarifierOutput)
    assert len(result.missing_fields) == 0
    assert len(result.questions) == 0


@pytest.mark.asyncio
async def test_clarifier_execute_handles_json_in_markdown(clarifier: Clarifier) -> None:
    """Test Clarifier handles JSON wrapped in markdown code blocks."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1", "Option 2"],
        },
    )

    # Mock LLM response with markdown code block
    mock_response = "```json\n" + json.dumps({
        "missing_fields": ["budget"],
        "questions": ["What is the budget?"],
    }) + "\n```"

    with patch("app.agents.clarifier.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await clarifier.execute(state)

    assert isinstance(result, ClarifierOutput)
    assert len(result.missing_fields) == 1


@pytest.mark.asyncio
async def test_clarifier_execute_invalid_json_raises_error(clarifier: Clarifier) -> None:
    """Test Clarifier raises AgentError for invalid JSON response."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1", "Option 2"],
        },
    )

    # Mock LLM response with invalid JSON
    mock_response = "This is not valid JSON"

    with patch("app.agents.clarifier.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        with pytest.raises(AgentError) as exc_info:
            await clarifier.execute(state)

        assert "Failed to parse LLM response as JSON" in str(exc_info.value)
        assert exc_info.value.agent_name == "clarifier"


@pytest.mark.asyncio
async def test_clarifier_execute_invalid_schema_raises_error(clarifier: Clarifier) -> None:
    """Test Clarifier raises ValidationError for invalid schema."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1", "Option 2"],
        },
    )

    # Mock LLM response with invalid schema (missing fields)
    mock_response = json.dumps({
        "missing_fields": ["budget"],
        # Missing "questions" field
    })

    with patch("app.agents.clarifier.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        with pytest.raises(ValidationError) as exc_info:
            await clarifier.execute(state)

        assert "ClarifierOutput validation failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_clarifier_execute_llm_error_raises_agent_error(clarifier: Clarifier) -> None:
    """Test Clarifier raises AgentError when LLM call fails."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1", "Option 2"],
        },
    )

    with patch("app.agents.clarifier.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(side_effect=Exception("LLM error"))
        mock_get_client.return_value = mock_client

        with pytest.raises(AgentError) as exc_info:
            await clarifier.execute(state)

        assert "LLM call failed" in str(exc_info.value)
        assert exc_info.value.agent_name == "clarifier"


@pytest.mark.asyncio
async def test_clarifier_execute_invalid_input_raises_agent_error(clarifier: Clarifier) -> None:
    """Test Clarifier raises AgentError when input cannot be built from PipelineState."""
    # State with invalid normalized_input (missing required fields)
    # Use None explicitly to trigger validation error
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": None,  # None will fail validation
            "options": None,  # None will fail validation
        },
    )

    with pytest.raises(AgentError) as exc_info:
        await clarifier.execute(state)

    assert "Failed to build ClarifierInput" in str(exc_info.value)
    assert exc_info.value.agent_name == "clarifier"
