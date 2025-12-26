"""Tests for Criteria Builder Agent."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.criteria_builder import CriteriaBuilder, normalize_weights
from app.core.exceptions import AgentError, ValidationError
from app.schemas.agents import CriteriaBuilderInput, CriteriaBuilderOutput
from app.schemas.decision import Criterion
from app.schemas.state import PipelineState


@pytest.fixture
def criteria_builder() -> CriteriaBuilder:
    """Create CriteriaBuilder agent instance."""
    return CriteriaBuilder()


def test_criteria_builder_name(criteria_builder: CriteriaBuilder) -> None:
    """Test CriteriaBuilder agent name."""
    assert criteria_builder.name == "criteria_builder"


def test_normalize_weights_proportional() -> None:
    """Test weight normalization with proportional weights."""
    criteria = [
        Criterion(name="cost", weight=0.3, rationale="Cost matters"),
        Criterion(name="quality", weight=0.2, rationale="Quality matters"),
        Criterion(name="speed", weight=0.1, rationale="Speed matters"),
    ]

    normalized = normalize_weights(criteria)

    total = sum(c.weight for c in normalized)
    assert abs(total - 1.0) < 0.001
    assert normalized[0].weight == pytest.approx(0.5, abs=0.001)  # 0.3 / 0.6
    assert normalized[1].weight == pytest.approx(0.333, abs=0.001)  # 0.2 / 0.6
    assert normalized[2].weight == pytest.approx(0.167, abs=0.001)  # 0.1 / 0.6


def test_normalize_weights_all_zeros() -> None:
    """Test weight normalization when all weights are zero."""
    criteria = [
        Criterion(name="cost", weight=0.0, rationale="Cost"),
        Criterion(name="quality", weight=0.0, rationale="Quality"),
    ]

    normalized = normalize_weights(criteria)

    total = sum(c.weight for c in normalized)
    assert abs(total - 1.0) < 0.001
    assert normalized[0].weight == pytest.approx(0.5, abs=0.001)
    assert normalized[1].weight == pytest.approx(0.5, abs=0.001)


def test_normalize_weights_empty_list() -> None:
    """Test weight normalization with empty list raises error."""
    with pytest.raises(ValueError, match="empty"):
        normalize_weights([])


def test_normalize_weights_already_normalized() -> None:
    """Test weight normalization when weights already sum to 1.0."""
    criteria = [
        Criterion(name="cost", weight=0.5, rationale="Cost"),
        Criterion(name="quality", weight=0.5, rationale="Quality"),
    ]

    normalized = normalize_weights(criteria)

    total = sum(c.weight for c in normalized)
    assert abs(total - 1.0) < 0.001
    assert normalized[0].weight == pytest.approx(0.5, abs=0.001)
    assert normalized[1].weight == pytest.approx(0.5, abs=0.001)


@pytest.mark.asyncio
async def test_criteria_builder_execute_generates_criteria(
    criteria_builder: CriteriaBuilder,
) -> None:
    """Test CriteriaBuilder generates criteria correctly."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Should we build feature X now or postpone it?",
            "options": ["Build now", "Postpone"],
            "constraints": {"budget": 50000},
        },
    )

    # Mock LLM response
    mock_response = json.dumps({
        "criteria": [
            {"name": "cost", "weight": 0.3, "rationale": "Cost is important"},
            {"name": "time_to_market", "weight": 0.4, "rationale": "Speed matters"},
            {"name": "quality", "weight": 0.3, "rationale": "Quality matters"},
        ],
    })

    with patch("app.agents.criteria_builder.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await criteria_builder.execute(state)

    assert isinstance(result, CriteriaBuilderOutput)
    assert len(result.criteria) == 3
    assert all(isinstance(c, Criterion) for c in result.criteria)

    # Verify weights are normalized
    total_weight = sum(c.weight for c in result.criteria)
    assert abs(total_weight - 1.0) < 0.001


@pytest.mark.asyncio
async def test_criteria_builder_execute_normalizes_weights(
    criteria_builder: CriteriaBuilder,
) -> None:
    """Test CriteriaBuilder normalizes weights to sum to 1.0."""
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

    # Mock LLM response with weights that don't sum to 1.0
    mock_response = json.dumps({
        "criteria": [
            {"name": "cost", "weight": 0.5, "rationale": "Cost"},
            {"name": "quality", "weight": 0.3, "rationale": "Quality"},
        ],
    })

    with patch("app.agents.criteria_builder.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await criteria_builder.execute(state)

    # Verify weights are normalized
    total_weight = sum(c.weight for c in result.criteria)
    assert abs(total_weight - 1.0) < 0.001
    # 0.5 / 0.8 = 0.625, 0.3 / 0.8 = 0.375
    assert result.criteria[0].weight == pytest.approx(0.625, abs=0.001)
    assert result.criteria[1].weight == pytest.approx(0.375, abs=0.001)


@pytest.mark.asyncio
async def test_criteria_builder_execute_handles_json_in_markdown(
    criteria_builder: CriteriaBuilder,
) -> None:
    """Test CriteriaBuilder handles JSON wrapped in markdown code blocks."""
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
        "criteria": [
            {"name": "cost", "weight": 0.5, "rationale": "Cost"},
            {"name": "quality", "weight": 0.5, "rationale": "Quality"},
        ],
    }) + "\n```"

    with patch("app.agents.criteria_builder.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await criteria_builder.execute(state)

    assert isinstance(result, CriteriaBuilderOutput)
    assert len(result.criteria) == 2


@pytest.mark.asyncio
async def test_criteria_builder_execute_invalid_json_raises_error(
    criteria_builder: CriteriaBuilder,
) -> None:
    """Test CriteriaBuilder raises AgentError for invalid JSON response."""
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

    mock_response = "This is not valid JSON"

    with patch("app.agents.criteria_builder.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        with pytest.raises(AgentError) as exc_info:
            await criteria_builder.execute(state)

        assert "Failed to parse LLM response as JSON" in str(exc_info.value)
        assert exc_info.value.agent_name == "criteria_builder"


@pytest.mark.asyncio
async def test_criteria_builder_execute_invalid_schema_raises_error(
    criteria_builder: CriteriaBuilder,
) -> None:
    """Test CriteriaBuilder raises ValidationError for invalid schema."""
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

    # Mock LLM response with invalid criterion structure (missing required fields)
    mock_response = json.dumps({
        "criteria": [
            {"name": "cost"},  # Missing weight and rationale
        ],
    })

    with patch("app.agents.criteria_builder.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        with pytest.raises(ValidationError) as exc_info:
            await criteria_builder.execute(state)

        # Should fail when building Criterion objects or validating output
        assert "validation failed" in str(exc_info.value).lower() or "Failed to build Criterion" in str(
            exc_info.value
        )


@pytest.mark.asyncio
async def test_criteria_builder_execute_empty_criteria_raises_error(
    criteria_builder: CriteriaBuilder,
) -> None:
    """Test CriteriaBuilder raises ValidationError for empty criteria list."""
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

    # Mock LLM response with empty criteria
    mock_response = json.dumps({"criteria": []})

    with patch("app.agents.criteria_builder.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        with pytest.raises(ValidationError) as exc_info:
            await criteria_builder.execute(state)

        assert "Weight normalization failed" in str(exc_info.value) or "validation failed" in str(
            exc_info.value
        ).lower()
