"""Request ID middleware for FastAPI."""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to extract or generate request_id and add to request state."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Extract or generate request_id and add to request state.

        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in chain

        Returns:
            Response with X-Request-ID header
        """
        # Extract or generate request_id
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Add to request state for access in handlers
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request_id to response headers
        response.headers["X-Request-ID"] = request_id

        return response
