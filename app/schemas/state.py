"""PipelineState Pydantic model."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class PipelineState(BaseModel):
    """
    Request-scoped state object for the deterministic pipeline.

    Contains all information needed for agent execution and response generation.
    Agents read from and write to this state object.
    """

    # Request identification and versioning
    request_id: str = Field(..., description="Unique request identifier")
    api_version: str = Field(..., description="API contract version (e.g., 'v1')")
    logic_version: str = Field(
        ..., description="Prompt bundle / agent pipeline version (e.g., '1.0.0')"
    )
    schema_version: str = Field(
        ..., description="JSON schema version (e.g., '1.0.0')"
    )

    # Normalized input (sanitized user input)
    normalized_input: dict[str, Any] = Field(
        ...,
        description="Sanitized and normalized user input",
    )

    # Agent outputs (will be replaced with typed models in later stories)
    clarifier_output: Optional[dict[str, Any]] = Field(
        default=None,
        description="Clarifier agent output (missing_fields, questions)",
    )
    criteria_builder_output: Optional[dict[str, Any]] = Field(
        default=None,
        description="Criteria Builder agent output (criteria with weights)",
    )
    bias_checker_output: Optional[dict[str, Any]] = Field(
        default=None,
        description="Bias Checker agent output (bias_findings)",
    )
    option_evaluator_output: Optional[dict[str, Any]] = Field(
        default=None,
        description="Option Evaluator agent output (scores per option per criterion)",
    )
    decision_synthesizer_output: Optional[dict[str, Any]] = Field(
        default=None,
        description="Decision Synthesizer agent output (winner, confidence, trade-offs)",
    )

    # Derived artifacts (extracted from agent outputs for easy access)
    derived_artifacts: dict[str, Any] = Field(
        default_factory=dict,
        description="Derived artifacts (criteria, weights, scores, biases)",
    )

    model_config = {"extra": "forbid"}


