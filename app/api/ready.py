"""GET /ready endpoint for readiness checks."""

import asyncio
from typing import Any

from fastapi import APIRouter, HTTPException, status
from redis.asyncio import Redis

from app.core.config import settings

router = APIRouter()


async def check_redis() -> bool:
    """
    Check Redis connectivity.

    Returns:
        bool: True if Redis is reachable, False otherwise
    """
    try:
        redis_client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password if settings.redis_password else None,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        await redis_client.ping()
        await redis_client.aclose()
        return True
    except Exception:
        return False


def check_openai_config() -> bool:
    """
    Check OpenAI API key is configured.

    Returns:
        bool: True if OpenAI API key is set, False otherwise
    """
    return bool(settings.openai_api_key and settings.openai_api_key != "")


@router.get("/ready")
async def ready() -> dict[str, Any]:
    """
    Readiness check endpoint for dependency verification.

    Checks:
    - Redis connectivity (for rate limiting)
    - OpenAI API key configuration

    Returns:
        dict: Status response with dependency checks
        - 200 OK if all dependencies are available
        - 503 Service Unavailable if any dependency is unavailable

    Raises:
        HTTPException: 503 if dependencies are unavailable
    """
    checks: dict[str, bool] = {}
    all_ready = True

    # Check Redis
    redis_ready = await check_redis()
    checks["redis"] = redis_ready
    if not redis_ready:
        all_ready = False

    # Check OpenAI configuration
    openai_ready = check_openai_config()
    checks["openai"] = openai_ready
    if not openai_ready:
        all_ready = False

    if not all_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "checks": checks,
            },
        )

    return {
        "status": "ready",
        "checks": checks,
    }

