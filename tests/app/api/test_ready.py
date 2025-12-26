"""Tests for ready endpoint."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_ready_endpoint_returns_200_when_all_dependencies_available() -> None:
    """Test that /ready returns 200 OK when all dependencies are available."""
    with patch("app.api.ready.check_redis", new_callable=AsyncMock) as mock_redis, patch(
        "app.api.ready.check_openai_config", return_value=True
    ) as mock_openai:
        mock_redis.return_value = True

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/ready")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert data["checks"]["redis"] is True
            assert data["checks"]["openai"] is True

        mock_redis.assert_called_once()
        mock_openai.assert_called_once()


@pytest.mark.asyncio
async def test_ready_endpoint_returns_503_when_redis_unavailable() -> None:
    """Test that /ready returns 503 when Redis is unavailable."""
    with patch("app.api.ready.check_redis", new_callable=AsyncMock) as mock_redis, patch(
        "app.api.ready.check_openai_config", return_value=True
    ) as mock_openai:
        mock_redis.return_value = False

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/ready")
            assert response.status_code == 503
            data = response.json()
            assert "detail" in data
            detail = data["detail"]
            assert detail["status"] == "not_ready"
            assert detail["checks"]["redis"] is False
            assert detail["checks"]["openai"] is True

        mock_redis.assert_called_once()
        mock_openai.assert_called_once()


@pytest.mark.asyncio
async def test_ready_endpoint_returns_503_when_openai_not_configured() -> None:
    """Test that /ready returns 503 when OpenAI API key is not configured."""
    with patch("app.api.ready.check_redis", new_callable=AsyncMock) as mock_redis, patch(
        "app.api.ready.check_openai_config", return_value=False
    ) as mock_openai:
        mock_redis.return_value = True

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/ready")
            assert response.status_code == 503
            data = response.json()
            assert "detail" in data
            detail = data["detail"]
            assert detail["status"] == "not_ready"
            assert detail["checks"]["redis"] is True
            assert detail["checks"]["openai"] is False

        mock_redis.assert_called_once()
        mock_openai.assert_called_once()


@pytest.mark.asyncio
async def test_ready_endpoint_returns_503_when_all_dependencies_unavailable() -> None:
    """Test that /ready returns 503 when all dependencies are unavailable."""
    with patch("app.api.ready.check_redis", new_callable=AsyncMock) as mock_redis, patch(
        "app.api.ready.check_openai_config", return_value=False
    ) as mock_openai:
        mock_redis.return_value = False

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/ready")
            assert response.status_code == 503
            data = response.json()
            assert "detail" in data
            detail = data["detail"]
            assert detail["status"] == "not_ready"
            assert detail["checks"]["redis"] is False
            assert detail["checks"]["openai"] is False

        mock_redis.assert_called_once()
        mock_openai.assert_called_once()

