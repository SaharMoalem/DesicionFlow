"""GET /health endpoint for liveness checks."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """
    Health check endpoint for liveness probes.

    Returns 200 OK if the service is running.
    This endpoint does not check dependencies (use /ready for that).

    Returns:
        dict: Simple status response with "status": "ok"
    """
    return {"status": "ok"}

