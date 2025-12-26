"""Pipeline runner/orchestrator."""

import uuid
from typing import Any

from app.core.config import settings
from app.core.exceptions import DecisionFlowError
from app.core.sanitization import sanitize_input
from app.orchestration.pipeline import PipelineExecutionError, execute_pipeline
from app.schemas.decision import DecisionRequest, DecisionResponse
from app.schemas.errors import ErrorCode, ErrorDetail, ErrorResponse
from app.schemas.state import PipelineState


async def run_pipeline(request: DecisionRequest, request_id: str | None = None) -> DecisionResponse:
    """
    Run the decision analysis pipeline.

    This is the main entry point for processing decision requests.
    It initializes the PipelineState, executes the pipeline, and returns
    the final DecisionResponse.

    Args:
        request: Decision request from API
        request_id: Optional request ID (generated if not provided)

    Returns:
        DecisionResponse with final recommendation

    Raises:
        DecisionFlowError: If pipeline execution fails
    """
    # Generate request_id if not provided
    if not request_id:
        request_id = str(uuid.uuid4())

    try:
        # Sanitize and normalize input
        normalized_input = sanitize_input(request.model_dump())

        # Initialize PipelineState
        state = PipelineState(
            request_id=request_id,
            api_version=settings.api_version,
            logic_version=settings.logic_version,
            schema_version=settings.schema_version,
            normalized_input=normalized_input,
        )

        # Execute pipeline
        response = await execute_pipeline(state)

        return response

    except PipelineExecutionError as e:
        # Transform pipeline error to DecisionFlowError
        raise DecisionFlowError(
            f"Pipeline execution failed: {str(e)}"
        ) from e
    except Exception as e:
        raise DecisionFlowError(
            f"Pipeline runner failed: {str(e)}"
        ) from e


