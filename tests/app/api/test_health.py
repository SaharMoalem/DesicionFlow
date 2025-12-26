"""Tests for health endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_200() -> None:
    """Test that /health returns 200 OK with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok"}


def test_health_endpoint_fast_response() -> None:
    """Test that /health responds quickly (no external dependencies)."""
    import time

    start = time.time()
    response = client.get("/health")
    elapsed = time.time() - start

    assert response.status_code == 200
    # Should be very fast (< 100ms) since it doesn't check dependencies
    assert elapsed < 0.1

