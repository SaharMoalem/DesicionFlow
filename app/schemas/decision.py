"""DecisionRequest, DecisionResponse schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.versioning import VersionMetadata


class DecisionRequest(BaseModel):
    """Request schema for decision analysis."""

    decision_context: str = Field(
        ...,
        description="Problem description and decision context",
        min_length=10,
        max_length=10000,
    )
    options: list[str] = Field(
        ...,
        description="Options to evaluate",
        min_length=2,
        max_length=20,
    )
    constraints: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional constraints (budget, timeline, etc.)",
    )
    criteria_preferences: Optional[list[str]] = Field(
        default=None,
        description="Optional user-specified criteria preferences",
    )
    context_metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional context metadata",
    )

    model_config = {"extra": "forbid"}


class Criterion(BaseModel):
    """Evaluation criterion with weight."""

    name: str = Field(..., description="Criterion name")
    weight: float = Field(
        ...,
        description="Criterion weight (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    rationale: str = Field(..., description="Rationale for this criterion")

    model_config = {"extra": "forbid"}


class BiasFinding(BaseModel):
    """Detected cognitive bias."""

    bias_type: str = Field(
        ...,
        description="Bias type (sunk_cost, confirmation, optimism, authority)",
    )
    description: str = Field(..., description="Description of the bias")
    evidence: str = Field(..., description="Evidence or context for the bias")

    model_config = {"extra": "forbid"}


class OptionScore(BaseModel):
    """Score for an option against a criterion."""

    criterion_name: str = Field(..., description="Criterion name")
    score: float = Field(
        ...,
        description="Score (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    justification: str = Field(..., description="Justification for this score")

    model_config = {"extra": "forbid"}


class OptionScores(BaseModel):
    """Scores for a single option across all criteria."""

    total_score: float = Field(
        ...,
        description="Weighted total score",
        ge=0.0,
        le=1.0,
    )
    breakdown: list[OptionScore] = Field(
        ...,
        description="Scores per criterion",
    )

    model_config = {"extra": "forbid"}


class ConfidenceBreakdown(BaseModel):
    """Confidence score breakdown by factor."""

    input_completeness: float = Field(
        ...,
        description="Input completeness factor (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    agent_agreement: float = Field(
        ...,
        description="Agent agreement factor (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    evidence_strength: float = Field(
        ...,
        description="Evidence strength factor (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    bias_impact: float = Field(
        ...,
        description="Bias impact factor (0.0 to 1.0, lower = more bias)",
        ge=0.0,
        le=1.0,
    )

    model_config = {"extra": "forbid"}


class DecisionResponse(BaseModel):
    """Response schema for decision analysis."""

    decision: str = Field(..., description="Decision identifier/description")
    options: list[str] = Field(..., description="Options that were evaluated")
    criteria: list[Criterion] = Field(..., description="Evaluation criteria with weights")
    scores: dict[str, OptionScores] = Field(
        ...,
        description="Scores per option (key = option name)",
    )
    winner: str = Field(..., description="Recommended option")
    confidence: float = Field(
        ...,
        description="Overall confidence score (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    confidence_breakdown: ConfidenceBreakdown = Field(
        ...,
        description="Confidence breakdown by factor",
    )
    biases_detected: list[BiasFinding] = Field(
        ...,
        description="Detected cognitive biases (separated from recommendation)",
    )
    trade_offs: list[dict[str, Any]] = Field(
        ...,
        description="Trade-offs between options",
    )
    assumptions: list[str] = Field(..., description="Documented assumptions")
    risks: list[dict[str, Any]] = Field(..., description="Identified risks")
    what_would_change_decision: list[str] = Field(
        ...,
        description="Factors that would change the decision",
    )
    meta: VersionMetadata = Field(..., description="Version metadata")
    request_id: str = Field(..., description="Request ID for correlation")

    model_config = {"extra": "forbid"}


