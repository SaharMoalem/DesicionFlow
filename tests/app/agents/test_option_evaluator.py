"""Tests for Option Evaluator Agent."""

import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.option_evaluator import (
    OptionEvaluator,
    calculate_weighted_total,
    normalize_score,
)
from app.core.exceptions import AgentError, ValidationError
from app.schemas.agents import OptionEvaluatorInput, OptionEvaluatorOutput
from app.schemas.decision import Criterion, OptionScore, OptionScores
from app.schemas.state import PipelineState


@pytest.fixture
def option_evaluator() -> OptionEvaluator:
    """Create OptionEvaluator agent instance."""
    return OptionEvaluator()


def test_option_evaluator_name(option_evaluator: OptionEvaluator) -> None:
    """Test OptionEvaluator agent name."""
    assert option_evaluator.name == "option_evaluator"


def test_normalize_score_within_range() -> None:
    """Test normalize_score with scores already in range."""
    assert normalize_score(0.5) == 0.5
    assert normalize_score(0.0) == 0.0
    assert normalize_score(1.0) == 1.0


def test_normalize_score_below_range() -> None:
    """Test normalize_score clamps scores below 0.0."""
    assert normalize_score(-0.5) == 0.0
    assert normalize_score(-10.0) == 0.0


def test_normalize_score_above_range() -> None:
    """Test normalize_score clamps scores above 1.0."""
    assert normalize_score(1.5) == 1.0
    assert normalize_score(10.0) == 1.0


def test_calculate_weighted_total() -> None:
    """Test calculate_weighted_total computes weighted sum correctly."""
    criteria = [
        Criterion(name="cost", weight=0.6, rationale="Cost matters"),
        Criterion(name="quality", weight=0.4, rationale="Quality matters"),
    ]

    option_scores = [
        OptionScore(criterion_name="cost", score=0.8, justification="Low cost"),
        OptionScore(criterion_name="quality", score=0.6, justification="Good quality"),
    ]

    total = calculate_weighted_total(option_scores, criteria)
    expected = 0.8 * 0.6 + 0.6 * 0.4  # 0.48 + 0.24 = 0.72
    assert abs(total - expected) < 0.001


@pytest.mark.asyncio
async def test_option_evaluator_execute_scores_options(
    option_evaluator: OptionEvaluator,
) -> None:
    """Test OptionEvaluator scores options correctly."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Should we build feature X?",
            "options": ["Build now", "Postpone"],
        },
        criteria_builder_output={
            "criteria": [
                {"name": "cost", "weight": 0.5, "rationale": "Cost matters"},
                {"name": "time", "weight": 0.5, "rationale": "Time matters"},
            ],
        },
    )

    # Mock LLM responses for each option
    mock_responses = [
        json.dumps({
            "scores": [
                {"criterion_name": "cost", "score": 0.7, "justification": "Moderate cost"},
                {"criterion_name": "time", "score": 0.8, "justification": "Fast delivery"},
            ],
        }),
        json.dumps({
            "scores": [
                {"criterion_name": "cost", "score": 0.9, "justification": "Lower cost"},
                {"criterion_name": "time", "score": 0.3, "justification": "Delayed delivery"},
            ],
        }),
    ]

    with patch("app.agents.option_evaluator.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        # Return different responses for each call
        mock_client.complete_with_prompt_template = AsyncMock(side_effect=mock_responses)
        mock_get_client.return_value = mock_client

        result = await option_evaluator.execute(state)

    assert isinstance(result, OptionEvaluatorOutput)
    assert len(result.scores) == 2
    assert "Build now" in result.scores
    assert "Postpone" in result.scores

    # Verify scores structure
    build_now_scores = result.scores["Build now"]
    assert isinstance(build_now_scores, OptionScores)
    assert len(build_now_scores.breakdown) == 2


@pytest.mark.asyncio
async def test_option_evaluator_execute_concurrent_scoring(
    option_evaluator: OptionEvaluator,
) -> None:
    """Test OptionEvaluator scores options concurrently."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1", "Option 2", "Option 3"],
        },
        criteria_builder_output={
            "criteria": [
                {"name": "cost", "weight": 1.0, "rationale": "Cost"},
            ],
        },
    )

    # Track call order to verify concurrency
    call_times = []

    async def mock_llm_call(*args, **kwargs):
        import time

        call_times.append(time.time())
        await asyncio.sleep(0.1)  # Simulate LLM call delay
        return json.dumps({
            "scores": [
                {"criterion_name": "cost", "score": 0.5, "justification": "Test"},
            ],
        })

    with patch("app.agents.option_evaluator.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(side_effect=mock_llm_call)
        mock_get_client.return_value = mock_client

        import time

        start_time = time.time()
        result = await option_evaluator.execute(state)
        end_time = time.time()

    # If sequential, would take ~0.3s (3 * 0.1s)
    # If concurrent, should take ~0.1s
    # Allow some margin for overhead
    assert (end_time - start_time) < 0.25  # Should be much faster than sequential
    assert len(result.scores) == 3


@pytest.mark.asyncio
async def test_option_evaluator_execute_normalizes_scores(
    option_evaluator: OptionEvaluator,
) -> None:
    """Test OptionEvaluator normalizes scores to 0.0-1.0 range."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1"],
        },
        criteria_builder_output={
            "criteria": [
                {"name": "cost", "weight": 1.0, "rationale": "Cost"},
            ],
        },
    )

    # Mock LLM response with score outside range
    mock_response = json.dumps({
        "scores": [
            {"criterion_name": "cost", "score": 1.5, "justification": "Test"},  # > 1.0
        ],
    })

    with patch("app.agents.option_evaluator.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await option_evaluator.execute(state)

    # Score should be normalized to 1.0
    score = result.scores["Option 1"].breakdown[0].score
    assert score == 1.0


@pytest.mark.asyncio
async def test_option_evaluator_execute_calculates_weighted_totals(
    option_evaluator: OptionEvaluator,
) -> None:
    """Test OptionEvaluator calculates weighted total scores."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1"],
        },
        criteria_builder_output={
            "criteria": [
                {"name": "cost", "weight": 0.6, "rationale": "Cost"},
                {"name": "quality", "weight": 0.4, "rationale": "Quality"},
            ],
        },
    )

    mock_response = json.dumps({
        "scores": [
            {"criterion_name": "cost", "score": 0.8, "justification": "Low cost"},
            {"criterion_name": "quality", "score": 0.6, "justification": "Good quality"},
        ],
    })

    with patch("app.agents.option_evaluator.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await option_evaluator.execute(state)

    # Weighted total: 0.8 * 0.6 + 0.6 * 0.4 = 0.48 + 0.24 = 0.72
    total_score = result.scores["Option 1"].total_score
    assert abs(total_score - 0.72) < 0.001


@pytest.mark.asyncio
async def test_option_evaluator_execute_missing_criteria_raises_error(
    option_evaluator: OptionEvaluator,
) -> None:
    """Test OptionEvaluator raises AgentError when criteria_builder_output is missing."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1"],
        },
        criteria_builder_output=None,
    )

    with pytest.raises(AgentError) as exc_info:
        await option_evaluator.execute(state)

    assert "Criteria Builder output not found" in str(exc_info.value)
    assert exc_info.value.agent_name == "option_evaluator"


@pytest.mark.asyncio
async def test_option_evaluator_execute_invalid_json_raises_error(
    option_evaluator: OptionEvaluator,
) -> None:
    """Test OptionEvaluator raises AgentError for invalid JSON response."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1"],
        },
        criteria_builder_output={
            "criteria": [
                {"name": "cost", "weight": 1.0, "rationale": "Cost"},
            ],
        },
    )

    mock_response = "This is not valid JSON"

    with patch("app.agents.option_evaluator.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        with pytest.raises(AgentError) as exc_info:
            await option_evaluator.execute(state)

        assert "Failed to parse LLM response as JSON" in str(exc_info.value)
        assert exc_info.value.agent_name == "option_evaluator"
