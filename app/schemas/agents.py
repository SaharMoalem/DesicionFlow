"""Agent input/output models."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.decision import (
    BiasFinding,
    ConfidenceBreakdown,
    Criterion,
    OptionScore,
    OptionScores,
)


class BiasType(str, Enum):
    """Enum for cognitive bias types."""

    SUNK_COST = "sunk_cost"
    CONFIRMATION = "confirmation"
    OPTIMISM = "optimism"
    AUTHORITY = "authority"


class ClarifierInput(BaseModel):
    """Input schema for Clarifier Agent."""

    decision_context: str = Field(..., description="Problem description and decision context")
    options: list[str] = Field(..., description="Options to evaluate")
    constraints: Optional[dict[str, Any]] = Field(
        default=None, description="Optional constraints (budget, timeline, etc.)"
    )
    criteria_preferences: Optional[list[str]] = Field(
        default=None, description="Optional user-specified criteria preferences"
    )
    context_metadata: Optional[dict[str, Any]] = Field(
        default=None, description="Additional context metadata"
    )

    model_config = {"extra": "forbid"}


class ClarifierOutput(BaseModel):
    """Output schema for Clarifier Agent."""

    missing_fields: list[str] = Field(
        ...,
        description="List of missing required input fields",
        min_length=0,
    )
    questions: list[str] = Field(
        ...,
        description="Structured questions to gather missing information",
        min_length=0,
    )

    model_config = {"extra": "forbid"}


class CriteriaBuilderInput(BaseModel):
    """Input schema for Criteria Builder Agent."""

    decision_context: str = Field(..., description="Problem description and decision context")
    options: list[str] = Field(..., description="Options to evaluate")
    constraints: Optional[dict[str, Any]] = Field(
        default=None, description="Optional constraints (budget, timeline, etc.)"
    )
    criteria_preferences: Optional[list[str]] = Field(
        default=None, description="Optional user-specified criteria preferences"
    )

    model_config = {"extra": "forbid"}


class CriteriaBuilderOutput(BaseModel):
    """Output schema for Criteria Builder Agent."""

    criteria: list[Criterion] = Field(
        ...,
        description="Evaluation criteria with weights and rationale",
        min_length=1,
    )

    model_config = {"extra": "forbid"}


class BiasCheckerInput(BaseModel):
    """Input schema for Bias Checker Agent."""

    decision_context: str = Field(..., description="Problem description and decision context")
    options: list[str] = Field(..., description="Options to evaluate")
    criteria: list[Criterion] = Field(..., description="Evaluation criteria from Criteria Builder")

    model_config = {"extra": "forbid"}


class BiasCheckerOutput(BaseModel):
    """Output schema for Bias Checker Agent."""

    bias_findings: list[BiasFinding] = Field(
        ...,
        description="Detected cognitive biases",
        min_length=0,
    )

    model_config = {"extra": "forbid"}


class OptionEvaluatorInput(BaseModel):
    """Input schema for Option Evaluator Agent."""

    decision_context: str = Field(..., description="Problem description and decision context")
    options: list[str] = Field(..., description="Options to evaluate")
    criteria: list[Criterion] = Field(..., description="Evaluation criteria from Criteria Builder")

    model_config = {"extra": "forbid"}


class OptionEvaluatorOutput(BaseModel):
    """Output schema for Option Evaluator Agent."""

    scores: dict[str, OptionScores] = Field(
        ...,
        description="Scores per option (key = option name, value = OptionScores)",
    )

    model_config = {"extra": "forbid"}


class DecisionSynthesizerInput(BaseModel):
    """Input schema for Decision Synthesizer Agent."""

    decision_context: str = Field(..., description="Problem description and decision context")
    options: list[str] = Field(..., description="Options to evaluate")
    criteria: list[Criterion] = Field(..., description="Evaluation criteria from Criteria Builder")
    scores: dict[str, OptionScores] = Field(
        ..., description="Scores per option from Option Evaluator"
    )
    bias_findings: list[BiasFinding] = Field(
        ..., description="Detected biases from Bias Checker"
    )

    model_config = {"extra": "forbid"}


class DecisionSynthesizerOutput(BaseModel):
    """Output schema for Decision Synthesizer Agent."""

    winner: str = Field(..., description="Recommended option")
    confidence: float = Field(
        ...,
        description="Overall confidence score (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    confidence_breakdown: ConfidenceBreakdown = Field(
        ..., description="Confidence breakdown by factor"
    )
    trade_offs: list[dict[str, Any]] = Field(
        ..., description="Trade-offs between options", min_length=0
    )
    assumptions: list[str] = Field(..., description="Documented assumptions", min_length=0)
    what_would_change_decision: list[str] = Field(
        ...,
        description="Factors that would change the decision",
        min_length=0,
    )

    model_config = {"extra": "forbid"}


