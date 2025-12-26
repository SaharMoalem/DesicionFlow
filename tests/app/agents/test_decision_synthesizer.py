"""Tests for Decision Synthesizer Agent."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.decision_synthesizer import DecisionSynthesizer
from app.core.exceptions import AgentError, ValidationError
from app.schemas.agents import DecisionSynthesizerInput, DecisionSynthesizerOutput
from app.schemas.decision import BiasFinding, Criterion, OptionScores
from app.schemas.state import PipelineState


@pytest.fixture
def decision_synthesizer() -> DecisionSynthesizer:
    """Create DecisionSynthesizer agent instance."""
    return DecisionSynthesizer()


def test_decision_synthesizer_name(decision_synthesizer: DecisionSynthesizer) -> None:
    """Test DecisionSynthesizer agent name."""
    assert decision_synthesizer.name == "decision_synthesizer"


@pytest.mark.asyncio
async def test_decision_synthesizer_execute_produces_recommendation(
    decision_synthesizer: DecisionSynthesizer,
) -> None:
    """Test DecisionSynthesizer produces final recommendation."""
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
        bias_checker_output={
            "bias_findings": [],
        },
        option_evaluator_output={
            "scores": {
                "Build now": {
                    "total_score": 0.75,
                    "breakdown": [
                        {
                            "criterion_name": "cost",
                            "score": 0.7,
                            "justification": "Moderate cost",
                        },
                        {
                            "criterion_name": "time",
                            "score": 0.8,
                            "justification": "Fast delivery",
                        },
                    ],
                },
                "Postpone": {
                    "total_score": 0.65,
                    "breakdown": [
                        {
                            "criterion_name": "cost",
                            "score": 0.9,
                            "justification": "Lower cost",
                        },
                        {
                            "criterion_name": "time",
                            "score": 0.4,
                            "justification": "Delayed delivery",
                        },
                    ],
                },
            },
        },
    )

    mock_response = json.dumps({
        "winner": "Build now",
        "confidence": 0.78,
        "confidence_breakdown": {
            "input_completeness": 0.8,
            "agent_agreement": 0.9,
            "evidence_strength": 0.75,
            "bias_impact": 0.85,
        },
        "trade_offs": [
            {"description": "Higher cost but faster delivery"},
        ],
        "assumptions": [
            "Assumes team has required expertise",
        ],
        "what_would_change_decision": [
            "If budget is reduced, Postpone becomes preferable",
        ],
    })

    with patch("app.agents.decision_synthesizer.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await decision_synthesizer.execute(state)

    assert isinstance(result, DecisionSynthesizerOutput)
    assert result.winner == "Build now"
    assert result.confidence == 0.78
    assert result.confidence_breakdown.input_completeness == 0.8
    assert len(result.trade_offs) == 1
    assert len(result.assumptions) == 1
    assert len(result.what_would_change_decision) == 1


@pytest.mark.asyncio
async def test_decision_synthesizer_execute_calculates_confidence(
    decision_synthesizer: DecisionSynthesizer,
) -> None:
    """Test DecisionSynthesizer calculates confidence score correctly."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1", "Option 2"],
        },
        criteria_builder_output={
            "criteria": [
                {"name": "cost", "weight": 1.0, "rationale": "Cost"},
            ],
        },
        bias_checker_output={
            "bias_findings": [
                {
                    "bias_type": "sunk_cost",
                    "description": "Previous investment influencing decision",
                    "evidence": "Mentioned $50k already spent",
                },
            ],
        },
        option_evaluator_output={
            "scores": {
                "Option 1": {
                    "total_score": 0.8,
                    "breakdown": [
                        {
                            "criterion_name": "cost",
                            "score": 0.8,
                            "justification": "Low cost",
                        },
                    ],
                },
                "Option 2": {
                    "total_score": 0.6,
                    "breakdown": [
                        {
                            "criterion_name": "cost",
                            "score": 0.6,
                            "justification": "Higher cost",
                        },
                    ],
                },
            },
        },
    )

    mock_response = json.dumps({
        "winner": "Option 1",
        "confidence": 0.65,
        "confidence_breakdown": {
            "input_completeness": 0.7,
            "agent_agreement": 0.8,
            "evidence_strength": 0.6,
            "bias_impact": 0.5,  # Lower due to detected bias
        },
        "trade_offs": [],
        "assumptions": [],
        "what_would_change_decision": [],
    })

    with patch("app.agents.decision_synthesizer.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await decision_synthesizer.execute(state)

    assert result.confidence == 0.65
    assert result.confidence_breakdown.bias_impact == 0.5  # Lower due to bias


@pytest.mark.asyncio
async def test_decision_synthesizer_execute_invalid_winner_raises_error(
    decision_synthesizer: DecisionSynthesizer,
) -> None:
    """Test DecisionSynthesizer raises ValidationError for invalid winner."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1", "Option 2"],
        },
        criteria_builder_output={
            "criteria": [
                {"name": "cost", "weight": 1.0, "rationale": "Cost"},
            ],
        },
        bias_checker_output={"bias_findings": []},
        option_evaluator_output={
            "scores": {
                "Option 1": {
                    "total_score": 0.8,
                    "breakdown": [
                        {
                            "criterion_name": "cost",
                            "score": 0.8,
                            "justification": "Test",
                        },
                    ],
                },
            },
        },
    )

    mock_response = json.dumps({
        "winner": "Invalid Option",  # Not in options list
        "confidence": 0.8,
        "confidence_breakdown": {
            "input_completeness": 0.8,
            "agent_agreement": 0.8,
            "evidence_strength": 0.8,
            "bias_impact": 0.8,
        },
        "trade_offs": [],
        "assumptions": [],
        "what_would_change_decision": [],
    })

    with patch("app.agents.decision_synthesizer.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        with pytest.raises(ValidationError) as exc_info:
            await decision_synthesizer.execute(state)

        assert "Winner" in str(exc_info.value) and "not one of the options" in str(
            exc_info.value
        )


@pytest.mark.asyncio
async def test_decision_synthesizer_execute_invalid_confidence_raises_error(
    decision_synthesizer: DecisionSynthesizer,
) -> None:
    """Test DecisionSynthesizer raises ValidationError for invalid confidence."""
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
        bias_checker_output={"bias_findings": []},
        option_evaluator_output={
            "scores": {
                "Option 1": {
                    "total_score": 0.8,
                    "breakdown": [
                        {
                            "criterion_name": "cost",
                            "score": 0.8,
                            "justification": "Test",
                        },
                    ],
                },
            },
        },
    )

    mock_response = json.dumps({
        "winner": "Option 1",
        "confidence": 1.5,  # Invalid: > 1.0
        "confidence_breakdown": {
            "input_completeness": 0.8,
            "agent_agreement": 0.8,
            "evidence_strength": 0.8,
            "bias_impact": 0.8,
        },
        "trade_offs": [],
        "assumptions": [],
        "what_would_change_decision": [],
    })

    with patch("app.agents.decision_synthesizer.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        with pytest.raises(ValidationError) as exc_info:
            await decision_synthesizer.execute(state)

        assert "Confidence score" in str(exc_info.value) and "between 0.0 and 1.0" in str(
            exc_info.value
        )


@pytest.mark.asyncio
async def test_decision_synthesizer_execute_missing_outputs_raises_error(
    decision_synthesizer: DecisionSynthesizer,
) -> None:
    """Test DecisionSynthesizer raises AgentError when required outputs are missing."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1"],
        },
        criteria_builder_output=None,  # Missing
        option_evaluator_output=None,  # Missing
    )

    with pytest.raises(AgentError) as exc_info:
        await decision_synthesizer.execute(state)

    assert "Criteria Builder output not found" in str(exc_info.value)
    assert exc_info.value.agent_name == "decision_synthesizer"


@pytest.mark.asyncio
async def test_decision_synthesizer_execute_with_biases(
    decision_synthesizer: DecisionSynthesizer,
) -> None:
    """Test DecisionSynthesizer handles bias findings correctly."""
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
        bias_checker_output={
            "bias_findings": [
                {
                    "bias_type": "sunk_cost",
                    "description": "Previous investment influencing decision",
                    "evidence": "Mentioned $50k already spent",
                },
                {
                    "bias_type": "confirmation",
                    "description": "Criteria favor preferred option",
                    "evidence": "Time-to-market weighted at 0.6",
                },
            ],
        },
        option_evaluator_output={
            "scores": {
                "Option 1": {
                    "total_score": 0.8,
                    "breakdown": [
                        {
                            "criterion_name": "cost",
                            "score": 0.8,
                            "justification": "Test",
                        },
                    ],
                },
            },
        },
    )

    mock_response = json.dumps({
        "winner": "Option 1",
        "confidence": 0.6,  # Lower due to biases
        "confidence_breakdown": {
            "input_completeness": 0.8,
            "agent_agreement": 0.7,
            "evidence_strength": 0.6,
            "bias_impact": 0.3,  # Low due to multiple biases
        },
        "trade_offs": [],
        "assumptions": [],
        "what_would_change_decision": [],
    })

    with patch("app.agents.decision_synthesizer.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await decision_synthesizer.execute(state)

    assert result.confidence == 0.6
    assert result.confidence_breakdown.bias_impact == 0.3  # Low due to biases
