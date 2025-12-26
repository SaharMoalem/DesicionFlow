"""Tests for pipeline orchestration."""

from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.decision import ConfidenceBreakdown

from app.core.exceptions import DecisionFlowError
from app.orchestration.pipeline import PipelineExecutionError, execute_pipeline
from app.orchestration.runner import run_pipeline
from app.schemas.decision import DecisionRequest
from app.schemas.state import PipelineState


@pytest.fixture
def sample_state() -> PipelineState:
    """Create sample PipelineState for testing."""
    return PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={
            "decision_context": "Should we build feature X?",
            "options": ["Build now", "Postpone"],
            "constraints": {"budget": 50000},
        },
    )


@pytest.mark.asyncio
async def test_execute_pipeline_fixed_order(sample_state: PipelineState) -> None:
    """Test pipeline executes agents in fixed order."""
    execution_order = []

    async def mock_clarifier_execute(state: PipelineState):
        execution_order.append("clarifier")
        from app.schemas.agents import ClarifierOutput

        return ClarifierOutput(missing_fields=[], questions=[])

    async def mock_criteria_builder_execute(state: PipelineState):
        execution_order.append("criteria_builder")
        from app.schemas.agents import CriteriaBuilderOutput
        from app.schemas.decision import Criterion

        return CriteriaBuilderOutput(
            criteria=[
                Criterion(name="cost", weight=0.5, rationale="Cost matters"),
                Criterion(name="time", weight=0.5, rationale="Time matters"),
            ]
        )

    async def mock_bias_checker_execute(state: PipelineState):
        execution_order.append("bias_checker")
        from app.schemas.agents import BiasCheckerOutput

        return BiasCheckerOutput(bias_findings=[])

    async def mock_option_evaluator_execute(state: PipelineState):
        execution_order.append("option_evaluator")
        from app.schemas.agents import OptionEvaluatorOutput
        from app.schemas.decision import OptionScore, OptionScores

        return OptionEvaluatorOutput(
            scores={
                "Build now": OptionScores(
                    total_score=0.75,
                    breakdown=[
                        OptionScore(
                            criterion_name="cost",
                            score=0.7,
                            justification="Moderate cost",
                        ),
                        OptionScore(
                            criterion_name="time",
                            score=0.8,
                            justification="Fast delivery",
                        ),
                    ],
                ),
                "Postpone": OptionScores(
                    total_score=0.65,
                    breakdown=[
                        OptionScore(
                            criterion_name="cost",
                            score=0.9,
                            justification="Lower cost",
                        ),
                        OptionScore(
                            criterion_name="time",
                            score=0.4,
                            justification="Delayed delivery",
                        ),
                    ],
                ),
            }
        )

    async def mock_decision_synthesizer_execute(state: PipelineState):
        execution_order.append("decision_synthesizer")
        from app.schemas.agents import DecisionSynthesizerOutput
        from app.schemas.decision import ConfidenceBreakdown

        return DecisionSynthesizerOutput(
            winner="Build now",
            confidence=0.78,
            confidence_breakdown=ConfidenceBreakdown(
                input_completeness=0.8,
                agent_agreement=0.9,
                evidence_strength=0.75,
                bias_impact=0.85,
            ),
            trade_offs=[],
            assumptions=[],
            what_would_change_decision=[],
        )

    with patch("app.orchestration.pipeline.Clarifier") as mock_clarifier, patch(
        "app.orchestration.pipeline.CriteriaBuilder"
    ) as mock_criteria_builder, patch(
        "app.orchestration.pipeline.BiasChecker"
    ) as mock_bias_checker, patch(
        "app.orchestration.pipeline.OptionEvaluator"
    ) as mock_option_evaluator, patch(
        "app.orchestration.pipeline.DecisionSynthesizer"
    ) as mock_decision_synthesizer:
        mock_clarifier.return_value.execute = AsyncMock(side_effect=mock_clarifier_execute)
        mock_criteria_builder.return_value.execute = AsyncMock(
            side_effect=mock_criteria_builder_execute
        )
        mock_bias_checker.return_value.execute = AsyncMock(side_effect=mock_bias_checker_execute)
        mock_option_evaluator.return_value.execute = AsyncMock(
            side_effect=mock_option_evaluator_execute
        )
        mock_decision_synthesizer.return_value.execute = AsyncMock(
            side_effect=mock_decision_synthesizer_execute
        )

        result = await execute_pipeline(sample_state)

    # Verify execution order
    assert execution_order == [
        "clarifier",
        "criteria_builder",
        "bias_checker",
        "option_evaluator",
        "decision_synthesizer",
    ]

    # Verify result
    assert result.winner == "Build now"
    assert result.confidence == 0.78


@pytest.mark.asyncio
async def test_execute_pipeline_writes_outputs_to_state(sample_state: PipelineState) -> None:
    """Test pipeline writes agent outputs to PipelineState."""
    from app.schemas.agents import (
        BiasCheckerOutput,
        ClarifierOutput,
        CriteriaBuilderOutput,
        DecisionSynthesizerOutput,
        OptionEvaluatorOutput,
    )
    from app.schemas.decision import Criterion, ConfidenceBreakdown, OptionScore, OptionScores

    async def mock_agent_execute(state: PipelineState):
        # Verify state is passed correctly
        assert state.request_id == "test_req"
        return None

    with patch("app.orchestration.pipeline.Clarifier") as mock_clarifier, patch(
        "app.orchestration.pipeline.CriteriaBuilder"
    ) as mock_criteria_builder, patch(
        "app.orchestration.pipeline.BiasChecker"
    ) as mock_bias_checker, patch(
        "app.orchestration.pipeline.OptionEvaluator"
    ) as mock_option_evaluator, patch(
        "app.orchestration.pipeline.DecisionSynthesizer"
    ) as mock_decision_synthesizer:
        mock_clarifier.return_value.execute = AsyncMock(
            return_value=ClarifierOutput(missing_fields=[], questions=[])
        )
        mock_criteria_builder.return_value.execute = AsyncMock(
            return_value=CriteriaBuilderOutput(
                criteria=[
                    Criterion(name="cost", weight=0.5, rationale="Cost"),
                    Criterion(name="time", weight=0.5, rationale="Time"),
                ]
            )
        )
        mock_bias_checker.return_value.execute = AsyncMock(
            return_value=BiasCheckerOutput(bias_findings=[])
        )
        mock_option_evaluator.return_value.execute = AsyncMock(
            return_value=OptionEvaluatorOutput(
                scores={
                    "Build now": OptionScores(
                        total_score=0.75,
                        breakdown=[
                            OptionScore(
                                criterion_name="cost",
                                score=0.7,
                                justification="Test",
                            ),
                        ],
                    ),
                }
            )
        )
        mock_decision_synthesizer.return_value.execute = AsyncMock(
            return_value=DecisionSynthesizerOutput(
                winner="Build now",
                confidence=0.78,
                confidence_breakdown=ConfidenceBreakdown(
                    input_completeness=0.8,
                    agent_agreement=0.9,
                    evidence_strength=0.75,
                    bias_impact=0.85,
                ),
                trade_offs=[],
                assumptions=[],
                what_would_change_decision=[],
            )
        )

        result = await execute_pipeline(sample_state)

    # Verify outputs were written to state
    assert sample_state.clarifier_output is not None
    assert sample_state.criteria_builder_output is not None
    assert sample_state.bias_checker_output is not None
    assert sample_state.option_evaluator_output is not None
    assert sample_state.decision_synthesizer_output is not None


@pytest.mark.asyncio
async def test_execute_pipeline_agent_error_raises_pipeline_error(
    sample_state: PipelineState,
) -> None:
    """Test pipeline raises PipelineExecutionError when agent fails."""
    from app.core.exceptions import AgentError

    with patch("app.orchestration.pipeline.Clarifier") as mock_clarifier:
        mock_clarifier.return_value.execute = AsyncMock(
            side_effect=AgentError("Test error", agent_name="clarifier")
        )

        with pytest.raises(PipelineExecutionError) as exc_info:
            await execute_pipeline(sample_state)

        assert "Agent clarifier failed" in str(exc_info.value)
        assert exc_info.value.agent_name == "clarifier"
        assert exc_info.value.request_id == "test_req"


@pytest.mark.asyncio
async def test_execute_pipeline_validation_error_raises_pipeline_error(
    sample_state: PipelineState,
) -> None:
    """Test pipeline raises PipelineExecutionError when validation fails."""
    from app.core.exceptions import ValidationError

    with patch("app.orchestration.pipeline.Clarifier") as mock_clarifier:
        mock_clarifier.return_value.execute = AsyncMock(
            side_effect=ValidationError("Schema validation failed")
        )

        with pytest.raises(PipelineExecutionError) as exc_info:
            await execute_pipeline(sample_state)

        assert "Schema validation failed" in str(exc_info.value)
        assert exc_info.value.request_id == "test_req"


@pytest.mark.asyncio
async def test_run_pipeline_complete_execution() -> None:
    """Test run_pipeline executes complete pipeline."""
    request = DecisionRequest(
        decision_context="Should we build feature X?",
        options=["Build now", "Postpone"],
        constraints={"budget": 50000},
    )

    # Mock all agents
    from app.schemas.agents import (
        BiasCheckerOutput,
        ClarifierOutput,
        CriteriaBuilderOutput,
        DecisionSynthesizerOutput,
        OptionEvaluatorOutput,
    )
    from app.schemas.decision import (
        Criterion,
        ConfidenceBreakdown,
        OptionScore,
        OptionScores,
    )

    with patch("app.orchestration.runner.execute_pipeline") as mock_execute:
        from app.schemas.decision import DecisionResponse
        from app.schemas.versioning import VersionMetadata

        mock_execute.return_value = DecisionResponse(
            decision="Should we build feature X?",
            options=["Build now", "Postpone"],
            criteria=[
                Criterion(name="cost", weight=0.5, rationale="Cost"),
                Criterion(name="time", weight=0.5, rationale="Time"),
            ],
            scores={
                "Build now": OptionScores(
                    total_score=0.75,
                    breakdown=[
                        OptionScore(
                            criterion_name="cost",
                            score=0.7,
                            justification="Test",
                        ),
                    ],
                ),
            },
            winner="Build now",
            confidence=0.78,
            confidence_breakdown=ConfidenceBreakdown(
                input_completeness=0.8,
                agent_agreement=0.9,
                evidence_strength=0.75,
                bias_impact=0.85,
            ),
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

        result = await run_pipeline(request, request_id="test_req")

    assert result.winner == "Build now"
    assert result.confidence == 0.78
    mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_run_pipeline_generates_request_id() -> None:
    """Test run_pipeline generates request_id if not provided."""
    request = DecisionRequest(
        decision_context="Should we build feature X?",
        options=["Build now", "Postpone"],
    )

    with patch("app.orchestration.runner.execute_pipeline") as mock_execute:
        from app.schemas.decision import DecisionResponse
        from app.schemas.versioning import VersionMetadata

        mock_execute.return_value = DecisionResponse(
            decision="Test",
            options=["Build now", "Postpone"],
            criteria=[],
            scores={},
            winner="Build now",
            confidence=0.8,
            confidence_breakdown=ConfidenceBreakdown(
                input_completeness=0.8,
                agent_agreement=0.8,
                evidence_strength=0.8,
                bias_impact=0.8,
            ),
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

        result = await run_pipeline(request)

    # Verify request_id was generated
    call_args = mock_execute.call_args[0][0]
    assert isinstance(call_args.request_id, str)
    assert len(call_args.request_id) > 0
