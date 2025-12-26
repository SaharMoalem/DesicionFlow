"""Tests for decision schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.decision import (
    BiasFinding,
    ConfidenceBreakdown,
    Criterion,
    DecisionRequest,
    DecisionResponse,
    OptionScore,
    OptionScores,
)
from app.schemas.versioning import VersionMetadata


def test_decision_request_valid() -> None:
    """Test DecisionRequest with valid data."""
    request = DecisionRequest(
        decision_context="Should we build feature X now or postpone it?",
        options=["Build now", "Postpone 3 months", "Postpone 6 months"],
        constraints={"budget": 50000, "timeline": "Q2 2024"},
        criteria_preferences=["time_to_market", "resource_availability"],
    )
    assert request.decision_context == "Should we build feature X now or postpone it?"
    assert len(request.options) == 3
    assert request.constraints is not None
    assert request.criteria_preferences is not None


def test_decision_request_min_length_validation() -> None:
    """Test DecisionRequest validates minimum length for decision_context."""
    with pytest.raises(ValidationError) as exc_info:
        DecisionRequest(
            decision_context="short",
            options=["Option 1", "Option 2"],
        )
    assert "at least 10 characters" in str(exc_info.value).lower()


def test_decision_request_min_options() -> None:
    """Test DecisionRequest requires at least 2 options."""
    with pytest.raises(ValidationError) as exc_info:
        DecisionRequest(
            decision_context="Should we do this?",
            options=["Only one option"],
        )
    assert "at least 2" in str(exc_info.value).lower()


def test_decision_request_max_options() -> None:
    """Test DecisionRequest limits maximum options."""
    with pytest.raises(ValidationError) as exc_info:
        DecisionRequest(
            decision_context="Should we do this?",
            options=[f"Option {i}" for i in range(21)],
        )
    assert "at most 20" in str(exc_info.value).lower()


def test_decision_request_extra_fields_forbidden() -> None:
    """Test DecisionRequest rejects extra fields."""
    with pytest.raises(ValidationError) as exc_info:
        DecisionRequest(
            decision_context="Should we do this?",
            options=["Option 1", "Option 2"],
            extra_field="not allowed",
        )
    assert "extra" in str(exc_info.value).lower() and "not permitted" in str(
        exc_info.value
    ).lower()


def test_criterion_valid() -> None:
    """Test Criterion with valid data."""
    criterion = Criterion(
        name="time_to_market",
        weight=0.4,
        rationale="Faster time to market is critical for competitive advantage",
    )
    assert criterion.name == "time_to_market"
    assert criterion.weight == 0.4
    assert criterion.weight >= 0.0
    assert criterion.weight <= 1.0


def test_criterion_weight_validation() -> None:
    """Test Criterion validates weight range."""
    with pytest.raises(ValidationError):
        Criterion(name="test", weight=1.5, rationale="test")

    with pytest.raises(ValidationError):
        Criterion(name="test", weight=-0.1, rationale="test")


def test_bias_finding_valid() -> None:
    """Test BiasFinding with valid data."""
    bias = BiasFinding(
        bias_type="sunk_cost",
        description="Previous investment influencing recommendation",
        evidence="User mentioned 'we already spent $50k on this'",
    )
    assert bias.bias_type == "sunk_cost"
    assert bias.description is not None
    assert bias.evidence is not None


def test_option_score_valid() -> None:
    """Test OptionScore with valid data."""
    score = OptionScore(
        criterion_name="cost",
        score=0.75,
        justification="Moderate cost with good value",
    )
    assert score.criterion_name == "cost"
    assert score.score == 0.75
    assert 0.0 <= score.score <= 1.0


def test_option_scores_valid() -> None:
    """Test OptionScores with valid data."""
    scores = OptionScores(
        total_score=0.82,
        breakdown=[
            OptionScore(
                criterion_name="cost",
                score=0.75,
                justification="Moderate cost",
            ),
            OptionScore(
                criterion_name="quality",
                score=0.90,
                justification="High quality",
            ),
        ],
    )
    assert scores.total_score == 0.82
    assert len(scores.breakdown) == 2


def test_confidence_breakdown_valid() -> None:
    """Test ConfidenceBreakdown with valid data."""
    breakdown = ConfidenceBreakdown(
        input_completeness=0.8,
        agent_agreement=0.9,
        evidence_strength=0.75,
        bias_impact=0.85,
    )
    assert breakdown.input_completeness == 0.8
    assert all(0.0 <= v <= 1.0 for v in breakdown.model_dump().values())


def test_decision_response_valid() -> None:
    """Test DecisionResponse with valid data."""
    response = DecisionResponse(
        decision="Choose cloud provider",
        options=["AWS", "GCP", "Azure"],
        criteria=[
            Criterion(name="cost", weight=0.3, rationale="Cost is important"),
            Criterion(name="scalability", weight=0.4, rationale="Need to scale"),
        ],
        scores={
            "AWS": OptionScores(
                total_score=0.82,
                breakdown=[
                    OptionScore(
                        criterion_name="cost",
                        score=0.75,
                        justification="Moderate cost",
                    ),
                ],
            ),
        },
        winner="AWS",
        confidence=0.78,
        confidence_breakdown=ConfidenceBreakdown(
            input_completeness=0.8,
            agent_agreement=0.9,
            evidence_strength=0.75,
            bias_impact=0.85,
        ),
        biases_detected=[
            BiasFinding(
                bias_type="optimism",
                description="Unjustified high confidence",
                evidence="High scores with weak evidence",
            ),
        ],
        trade_offs=[],
        assumptions=["Team has AWS experience"],
        risks=[],
            what_would_change_decision=["If budget increases by 20%"],
            meta=VersionMetadata(
                api_version="v1", logic_version="1.0.0", schema_version="1.0.0"
            ),
            request_id="req_123",
    )
    assert response.decision == "Choose cloud provider"
    assert response.winner == "AWS"
    assert response.confidence == 0.78
    assert len(response.biases_detected) == 1
    assert response.request_id == "req_123"


def test_decision_response_confidence_validation() -> None:
    """Test DecisionResponse validates confidence range."""
    with pytest.raises(ValidationError):
        DecisionResponse(
            decision="test",
            options=["opt1", "opt2"],
            criteria=[],
            scores={},
            winner="opt1",
            confidence=1.5,  # Invalid: > 1.0
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
                api_version="v1", logic_version="1.0.0", schema_version="1.0.0"
            ),
            request_id="req_123",
        )

