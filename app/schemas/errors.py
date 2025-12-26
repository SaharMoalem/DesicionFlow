"""ErrorResponse, error codes."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """Error code categories."""

    # Validation Errors
    INVALID_REQUEST = "INVALID_REQUEST"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_OPTION_COUNT = "INVALID_OPTION_COUNT"
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"

    # Processing Errors
    SCHEMA_VALIDATION_FAILED = "SCHEMA_VALIDATION_FAILED"
    AGENT_TIMEOUT = "AGENT_TIMEOUT"
    PIPELINE_ERROR = "PIPELINE_ERROR"
    INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"

    # System Errors
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    # Authentication/Authorization Errors
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_API_KEY = "INVALID_API_KEY"


class ErrorDetail(BaseModel):
    """Error detail structure."""

    code: ErrorCode = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(
        default=None, description="Additional error context"
    )

    model_config = {"extra": "forbid"}


class ErrorResponse(BaseModel):
    """Standardized error response envelope."""

    error: ErrorDetail = Field(..., description="Error information")
    request_id: str = Field(..., description="Request ID for correlation")

    model_config = {"extra": "forbid"}


