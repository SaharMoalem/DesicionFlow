"""Tests for Bias Checker Agent."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.bias_checker import BiasChecker, validate_bias_type
from app.core.exceptions import AgentError, ValidationError
from app.schemas.agents import BiasCheckerInput, BiasCheckerOutput, BiasType
from app.schemas.decision import BiasFinding
from app.schemas.state import PipelineState


@pytest.fixture
def bias_checker() -> BiasChecker:
    """Create BiasChecker agent instance."""
    return BiasChecker()


def test_bias_checker_name(bias_checker: BiasChecker) -> None:
    """Test BiasChecker agent name."""
    assert bias_checker.name == "bias_checker"


def test_validate_bias_type_valid() -> None:
    """Test validate_bias_type with valid bias types."""
    assert validate_bias_type("sunk_cost") == "sunk_cost"
    assert validate_bias_type("confirmation") == "confirmation"
    assert validate_bias_type("optimism") == "optimism"
    assert validate_bias_type("authority") == "authority"


def test_validate_bias_type_case_insensitive() -> None:
    """Test validate_bias_type handles case-insensitive input."""
    assert validate_bias_type("SUNK_COST") == "sunk_cost"
    assert validate_bias_type("Confirmation") == "confirmation"


def test_validate_bias_type_invalid() -> None:
    """Test validate_bias_type raises ValidationError for invalid types."""
    with pytest.raises(ValidationError, match="Invalid bias_type"):
        validate_bias_type("invalid_bias")


@pytest.mark.asyncio
async def test_bias_checker_execute_detects_sunk_cost_bias(
    bias_checker: BiasChecker,
) -> None:
    """Test BiasChecker detects sunk cost bias."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "We already spent $50k on this project. Should we continue?",
            "options": ["Continue", "Stop"],
        },
        criteria_builder_output={
            "criteria": [
                {"name": "cost", "weight": 0.5, "rationale": "Cost matters"},
            ],
        },
    )

    mock_response = json.dumps({
        "bias_findings": [
            {
                "bias_type": "sunk_cost",
                "description": "Previous investment influencing recommendation",
                "evidence": "Mentioned 'we already spent $50k'",
            },
        ],
    })

    with patch("app.agents.bias_checker.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await bias_checker.execute(state)

    assert isinstance(result, BiasCheckerOutput)
    assert len(result.bias_findings) == 1
    assert result.bias_findings[0].bias_type == "sunk_cost"


@pytest.mark.asyncio
async def test_bias_checker_execute_detects_confirmation_bias(
    bias_checker: BiasChecker,
) -> None:
    """Test BiasChecker detects confirmation bias."""
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
                {"name": "time_to_market", "weight": 0.6, "rationale": "Speed matters"},
                {"name": "cost", "weight": 0.4, "rationale": "Cost matters"},
            ],
        },
    )

    mock_response = json.dumps({
        "bias_findings": [
            {
                "bias_type": "confirmation",
                "description": "Criteria weights favor the 'build now' option",
                "evidence": "Time-to-market weighted at 0.6, which heavily favors the preferred option",
            },
        ],
    })

    with patch("app.agents.bias_checker.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await bias_checker.execute(state)

    assert isinstance(result, BiasCheckerOutput)
    assert len(result.bias_findings) == 1
    assert result.bias_findings[0].bias_type == "confirmation"


@pytest.mark.asyncio
async def test_bias_checker_execute_detects_optimism_bias(
    bias_checker: BiasChecker,
) -> None:
    """Test BiasChecker detects optimism bias."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "This will definitely succeed!",
            "options": ["Option 1", "Option 2"],
        },
        criteria_builder_output={
            "criteria": [
                {"name": "success_probability", "weight": 0.5, "rationale": "Likelihood of success"},
            ],
        },
    )

    mock_response = json.dumps({
        "bias_findings": [
            {
                "bias_type": "optimism",
                "description": "Unjustified high confidence without evidence",
                "evidence": "Used 'definitely' without supporting evidence",
            },
        ],
    })

    with patch("app.agents.bias_checker.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await bias_checker.execute(state)

    assert isinstance(result, BiasCheckerOutput)
    assert len(result.bias_findings) == 1
    assert result.bias_findings[0].bias_type == "optimism"


@pytest.mark.asyncio
async def test_bias_checker_execute_detects_authority_bias(
    bias_checker: BiasChecker,
) -> None:
    """Test BiasChecker detects authority bias."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Google recommends this approach, so we should do it",
            "options": ["Follow Google's approach", "Alternative approach"],
        },
        criteria_builder_output={
            "criteria": [
                {"name": "expert_recommendation", "weight": 0.8, "rationale": "Expert opinion"},
            ],
        },
    )

    mock_response = json.dumps({
        "bias_findings": [
            {
                "bias_type": "authority",
                "description": "Over-reliance on brand name without independent evaluation",
                "evidence": "Mentioned 'Google recommends' as primary justification",
            },
        ],
    })

    with patch("app.agents.bias_checker.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await bias_checker.execute(state)

    assert isinstance(result, BiasCheckerOutput)
    assert len(result.bias_findings) == 1
    assert result.bias_findings[0].bias_type == "authority"


@pytest.mark.asyncio
async def test_bias_checker_execute_no_biases_detected(
    bias_checker: BiasChecker,
) -> None:
    """Test BiasChecker returns empty list when no biases detected."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Objective decision context with balanced criteria",
            "options": ["Option 1", "Option 2"],
        },
        criteria_builder_output={
            "criteria": [
                {"name": "cost", "weight": 0.5, "rationale": "Cost matters"},
                {"name": "quality", "weight": 0.5, "rationale": "Quality matters"},
            ],
        },
    )

    mock_response = json.dumps({"bias_findings": []})

    with patch("app.agents.bias_checker.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await bias_checker.execute(state)

    assert isinstance(result, BiasCheckerOutput)
    assert len(result.bias_findings) == 0


@pytest.mark.asyncio
async def test_bias_checker_execute_multiple_biases(
    bias_checker: BiasChecker,
) -> None:
    """Test BiasChecker detects multiple biases."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "We already spent $50k and Google says this is the best approach",
            "options": ["Continue", "Stop"],
        },
        criteria_builder_output={
            "criteria": [
                {"name": "cost", "weight": 0.5, "rationale": "Cost"},
            ],
        },
    )

    mock_response = json.dumps({
        "bias_findings": [
            {
                "bias_type": "sunk_cost",
                "description": "Previous investment influencing decision",
                "evidence": "Mentioned '$50k already spent'",
            },
            {
                "bias_type": "authority",
                "description": "Over-reliance on brand name",
                "evidence": "Mentioned 'Google says'",
            },
        ],
    })

    with patch("app.agents.bias_checker.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        result = await bias_checker.execute(state)

    assert isinstance(result, BiasCheckerOutput)
    assert len(result.bias_findings) == 2
    assert result.bias_findings[0].bias_type == "sunk_cost"
    assert result.bias_findings[1].bias_type == "authority"


@pytest.mark.asyncio
async def test_bias_checker_execute_invalid_bias_type_raises_error(
    bias_checker: BiasChecker,
) -> None:
    """Test BiasChecker raises ValidationError for invalid bias_type."""
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
                {"name": "cost", "weight": 0.5, "rationale": "Cost"},
            ],
        },
    )

    mock_response = json.dumps({
        "bias_findings": [
            {
                "bias_type": "invalid_bias",
                "description": "Test",
                "evidence": "Test",
            },
        ],
    })

    with patch("app.agents.bias_checker.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        with pytest.raises(ValidationError) as exc_info:
            await bias_checker.execute(state)

        assert "Invalid bias_type" in str(exc_info.value)


@pytest.mark.asyncio
async def test_bias_checker_execute_missing_criteria_builder_output_raises_error(
    bias_checker: BiasChecker,
) -> None:
    """Test BiasChecker raises AgentError when criteria_builder_output is missing."""
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Test",
            "options": ["Option 1", "Option 2"],
        },
        criteria_builder_output=None,
    )

    with pytest.raises(AgentError) as exc_info:
        await bias_checker.execute(state)

    assert "Criteria Builder output not found" in str(exc_info.value)
    assert exc_info.value.agent_name == "bias_checker"
