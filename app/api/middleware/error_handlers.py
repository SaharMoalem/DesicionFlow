"""Global exception handlers for FastAPI."""

import logging
import uuid
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import (
    AgentError,
    DecisionFlowError,
    LLMError,
    ValidationError,
)
from app.schemas.errors import ErrorCode, ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    """
    Extract or generate request_id from request.

    Checks for X-Request-ID header first, then generates a new UUID.

    Args:
        request: FastAPI request object

    Returns:
        Request ID string
    """
    # Check for X-Request-ID header
    request_id = request.headers.get("X-Request-ID")
    if request_id:
        return request_id

    # Generate new UUID if not present
    return str(uuid.uuid4())


def transform_exception_to_error_response(
    exc: Exception, request_id: str, agent_name: str | None = None, step: str | None = None
) -> tuple[ErrorResponse, int]:
    """
    Transform an exception to ErrorResponse format.

    Args:
        exc: Exception to transform
        request_id: Request ID for correlation
        agent_name: Optional agent name for context
        step: Optional pipeline step for context

    Returns:
        Tuple of (ErrorResponse, HTTP status code)
    """
    # Build error details
    error_details: dict[str, Any] = {
        "error_type": type(exc).__name__,
    }
    if agent_name:
        error_details["agent"] = agent_name
    if step:
        error_details["step"] = step

    # Map exception types to error codes and status codes
    if isinstance(exc, ValidationError):
        error_code = ErrorCode.INVALID_REQUEST
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, PydanticValidationError):
        error_code = ErrorCode.INVALID_REQUEST
        status_code = status.HTTP_400_BAD_REQUEST
        error_details["validation_errors"] = [str(err) for err in exc.errors()]
    elif isinstance(exc, AgentError):
        error_code = ErrorCode.PIPELINE_ERROR
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if exc.agent_name:
            error_details["agent"] = exc.agent_name
    elif isinstance(exc, LLMError):
        if exc.status_code == 429:
            error_code = ErrorCode.RATE_LIMIT_EXCEEDED
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
        elif exc.status_code == 503:
            error_code = ErrorCode.SERVICE_UNAVAILABLE
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            error_code = ErrorCode.SERVICE_UNAVAILABLE
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, DecisionFlowError):
        error_code = ErrorCode.PIPELINE_ERROR
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        error_code = ErrorCode.INTERNAL_ERROR
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    error_response = ErrorResponse(
        error=ErrorDetail(
            code=error_code,
            message=str(exc) or "An error occurred",
            details=error_details,
        ),
        request_id=request_id,
    )

    return error_response, status_code


async def validation_exception_handler(request: Request, exc: PydanticValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request object
        exc: Validation exception

    Returns:
        JSONResponse with ErrorResponse format
    """
    request_id = get_request_id(request)

    # Log error with full context
    logger.error(
        "Validation error",
        extra={
            "request_id": request_id,
            "error_type": type(exc).__name__,
            "validation_errors": [str(err) for err in exc.errors()],
        },
    )

    error_response, status_code = transform_exception_to_error_response(exc, request_id)

    return JSONResponse(
        content=error_response.model_dump(),
        status_code=status_code,
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle custom ValidationError exceptions.

    Args:
        request: FastAPI request object
        exc: Validation exception

    Returns:
        JSONResponse with ErrorResponse format
    """
    request_id = get_request_id(request)

    # Log error with full context
    logger.error(
        "Validation error",
        extra={
            "request_id": request_id,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        },
    )

    error_response, status_code = transform_exception_to_error_response(exc, request_id)

    return JSONResponse(
        content=error_response.model_dump(),
        status_code=status_code,
    )


async def agent_error_handler(request: Request, exc: AgentError) -> JSONResponse:
    """
    Handle AgentError exceptions.

    Args:
        request: FastAPI request object
        exc: Agent exception

    Returns:
        JSONResponse with ErrorResponse format
    """
    request_id = get_request_id(request)

    # Log error with full context
    logger.error(
        "Agent error",
        extra={
            "request_id": request_id,
            "error_type": type(exc).__name__,
            "agent_name": exc.agent_name,
            "error_message": str(exc),
        },
    )

    error_response, status_code = transform_exception_to_error_response(
        exc, request_id, agent_name=exc.agent_name
    )

    return JSONResponse(
        content=error_response.model_dump(),
        status_code=status_code,
    )


async def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
    """
    Handle LLMError exceptions.

    Args:
        request: FastAPI request object
        exc: LLM exception

    Returns:
        JSONResponse with ErrorResponse format
    """
    request_id = get_request_id(request)

    # Log error with full context
    logger.error(
        "LLM error",
        extra={
            "request_id": request_id,
            "error_type": type(exc).__name__,
            "retryable": exc.retryable,
            "status_code": exc.status_code,
            "error_message": str(exc),
        },
    )

    error_response, status_code = transform_exception_to_error_response(exc, request_id)

    return JSONResponse(
        content=error_response.model_dump(),
        status_code=status_code,
    )


async def decision_flow_error_handler(request: Request, exc: DecisionFlowError) -> JSONResponse:
    """
    Handle DecisionFlowError exceptions.

    Args:
        request: FastAPI request object
        exc: DecisionFlow exception

    Returns:
        JSONResponse with ErrorResponse format
    """
    request_id = get_request_id(request)

    # Log error with full context
    logger.error(
        "DecisionFlow error",
        extra={
            "request_id": request_id,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        },
    )

    error_response, status_code = transform_exception_to_error_response(exc, request_id)

    return JSONResponse(
        content=error_response.model_dump(),
        status_code=status_code,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all other unhandled exceptions.

    Args:
        request: FastAPI request object
        exc: Exception

    Returns:
        JSONResponse with ErrorResponse format
    """
    request_id = get_request_id(request)

    # Log error with full context
    logger.exception(
        "Unhandled exception",
        extra={
            "request_id": request_id,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        },
        exc_info=exc,
    )

    error_response, status_code = transform_exception_to_error_response(exc, request_id)

    return JSONResponse(
        content=error_response.model_dump(),
        status_code=status_code,
    )

