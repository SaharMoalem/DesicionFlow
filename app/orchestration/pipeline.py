"""Deterministic pipeline execution."""

from typing import Any

from app.agents.bias_checker import BiasChecker
from app.agents.clarifier import Clarifier
from app.agents.criteria_builder import CriteriaBuilder
from app.agents.decision_synthesizer import DecisionSynthesizer
from app.agents.option_evaluator import OptionEvaluator
from app.core.exceptions import AgentError, ValidationError
from app.schemas.agents import (
    BiasCheckerOutput,
    ClarifierOutput,
    CriteriaBuilderOutput,
    DecisionSynthesizerOutput,
    OptionEvaluatorOutput,
)
from app.schemas.decision import DecisionResponse
from app.schemas.state import PipelineState
from app.schemas.versioning import VersionMetadata


class PipelineExecutionError(Exception):
    """Exception raised during pipeline execution."""

    def __init__(self, message: str, agent_name: str | None = None, request_id: str | None = None):
        super().__init__(message)
        self.agent_name = agent_name
        self.request_id = request_id


async def execute_pipeline(state: PipelineState) -> DecisionResponse:
    """
    Execute the deterministic decision analysis pipeline.

    Agents execute in fixed order:
    1. Clarifier → identifies missing inputs
    2. Criteria Builder → generates weighted criteria
    3. Bias Checker → detects cognitive biases
    4. Option Evaluator → scores each option
    5. Decision Synthesizer → produces final recommendation

    Args:
        state: Initial pipeline state with normalized_input

    Returns:
        DecisionResponse with final recommendation

    Raises:
        PipelineExecutionError: If pipeline execution fails
    """
    # Initialize agents (in execution order)
    clarifier = Clarifier()
    criteria_builder = CriteriaBuilder()
    bias_checker = BiasChecker()
    option_evaluator = OptionEvaluator()
    decision_synthesizer = DecisionSynthesizer()

    try:
        # Step 1: Clarifier Agent
        clarifier_output: ClarifierOutput = await clarifier.execute(state)
        state.clarifier_output = clarifier_output.model_dump()

        # Check if Clarifier identified missing information
        if clarifier_output.missing_fields or clarifier_output.questions:
            # Return NEEDS_INFO status (this is the only degraded output allowed)
            # Note: In a full implementation, this would return a special response type
            # For now, we'll continue but this should be handled by the API layer
            pass

        # Step 2: Criteria Builder Agent
        criteria_builder_output: CriteriaBuilderOutput = await criteria_builder.execute(state)
        state.criteria_builder_output = criteria_builder_output.model_dump()

        # Step 3: Bias Checker Agent
        bias_checker_output: BiasCheckerOutput = await bias_checker.execute(state)
        state.bias_checker_output = bias_checker_output.model_dump()

        # Step 4: Option Evaluator Agent
        option_evaluator_output: OptionEvaluatorOutput = await option_evaluator.execute(state)
        state.option_evaluator_output = option_evaluator_output.model_dump()

        # Step 5: Decision Synthesizer Agent
        decision_synthesizer_output: DecisionSynthesizerOutput = (
            await decision_synthesizer.execute(state)
        )
        state.decision_synthesizer_output = decision_synthesizer_output.model_dump()

        # Build DecisionResponse from all agent outputs
        response = _build_decision_response(state, decision_synthesizer_output)

        return response

    except AgentError as e:
        raise PipelineExecutionError(
            f"Agent {e.agent_name} failed: {str(e)}",
            agent_name=e.agent_name,
            request_id=state.request_id,
        ) from e
    except ValidationError as e:
        raise PipelineExecutionError(
            f"Schema validation failed: {str(e)}",
            request_id=state.request_id,
        ) from e
    except Exception as e:
        raise PipelineExecutionError(
            f"Pipeline execution failed: {str(e)}",
            request_id=state.request_id,
        ) from e


def _build_decision_response(
    state: PipelineState, synthesizer_output: DecisionSynthesizerOutput
) -> DecisionResponse:
    """
    Build DecisionResponse from PipelineState and DecisionSynthesizer output.

    Args:
        state: Pipeline state with all agent outputs
        synthesizer_output: Decision Synthesizer output

    Returns:
        DecisionResponse
    """
    from app.schemas.decision import BiasFinding, Criterion, OptionScores

    # Extract criteria from criteria_builder_output
    criteria_dicts = state.criteria_builder_output.get("criteria", []) if state.criteria_builder_output else []
    criteria = [
        Criterion(
            name=criterion["name"],
            weight=criterion["weight"],
            rationale=criterion["rationale"],
        )
        for criterion in criteria_dicts
    ]

    # Extract scores from option_evaluator_output
    scores_dict = state.option_evaluator_output.get("scores", {}) if state.option_evaluator_output else {}
    scores: dict[str, OptionScores] = {}
    for option_name, scores_data in scores_dict.items():
        scores[option_name] = OptionScores(**scores_data)

    # Extract bias findings from bias_checker_output
    bias_findings_dicts = (
        state.bias_checker_output.get("bias_findings", []) if state.bias_checker_output else []
    )
    bias_findings = [BiasFinding(**finding) for finding in bias_findings_dicts]

    # Extract options from normalized_input
    options = state.normalized_input.get("options", [])

    # Build DecisionResponse
    response = DecisionResponse(
        decision=state.normalized_input.get("decision_context", ""),
        options=options,
        criteria=criteria,
        scores=scores,
        winner=synthesizer_output.winner,
        confidence=synthesizer_output.confidence,
        confidence_breakdown=synthesizer_output.confidence_breakdown,
        biases_detected=bias_findings,
        trade_offs=synthesizer_output.trade_offs,
        assumptions=synthesizer_output.assumptions,
        risks=[],  # Will be populated in future stories
        what_would_change_decision=synthesizer_output.what_would_change_decision,
        meta=VersionMetadata(
            api_version=state.api_version,
            logic_version=state.logic_version,
            schema_version=state.schema_version,
        ),
        request_id=state.request_id,
    )

    return response


