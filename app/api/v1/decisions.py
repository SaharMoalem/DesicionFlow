"""POST /v1/decisions/analyze endpoint."""

from fastapi import APIRouter, Request, status

from app.core.exceptions import ValidationError
from app.orchestration.runner import run_pipeline
from app.schemas.decision import DecisionRequest, DecisionResponse
from app.validation.service import validate_request, validate_response

router = APIRouter(prefix="/v1/decisions", tags=["decisions"])


@router.post(
    "/analyze",
    response_model=DecisionResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_decision(
    request_body: DecisionRequest, request: Request
) -> DecisionResponse:
    """
    Analyze a decision request and return a structured recommendation.

    This endpoint processes decision requests through a deterministic
    multi-agent pipeline, returning a structured decision analysis with
    recommendations, bias detection, and confidence scores.

    Args:
        request_body: Decision request containing context, options, and constraints
        request: FastAPI request object (for accessing request_id from middleware)

    Returns:
        DecisionResponse with structured analysis and recommendation

    Raises:
        ValidationError: If request or response validation fails
        DecisionFlowError: If pipeline execution fails
    """
    # Get request_id from middleware (set by RequestIDMiddleware)
    request_id = request.state.request_id

    # Validate request payload immediately on receipt
    validation_result = await validate_request(request_body.model_dump(), attempt_repair=False)
    if not validation_result.is_valid:
        raise ValidationError(
            f"Request validation failed: {', '.join(validation_result.errors)}"
        )

    # Call pipeline orchestration to process the request
    response = await run_pipeline(request_body, request_id=request_id)

    # Validate response payload before returning
    response_validation = await validate_response(response.model_dump(), attempt_repair=False)
    if not response_validation.is_valid:
        raise ValidationError(
            f"Response validation failed: {', '.join(response_validation.errors)}"
        )

    # Ensure request_id is in response (should already be set by pipeline)
    if response.request_id != request_id:
        response.request_id = request_id

    return response


