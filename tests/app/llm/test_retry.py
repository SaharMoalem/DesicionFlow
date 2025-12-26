"""Tests for retry logic."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from openai import APIError, APITimeoutError, RateLimitError

from app.core.exceptions import LLMError, LLMRateLimitError, LLMTimeoutError
from app.llm.retry import is_retryable_error, retry_with_backoff


def test_is_retryable_error_timeout() -> None:
    """Test that timeout errors are retryable."""
    mock_request = MagicMock()
    assert is_retryable_error(APITimeoutError(request=mock_request)) is True
    assert is_retryable_error(TimeoutError()) is True
    assert is_retryable_error(asyncio.TimeoutError()) is True


def test_is_retryable_error_rate_limit_not_retryable() -> None:
    """Test that rate limit errors are NOT retryable."""
    mock_response = MagicMock()
    mock_response.request = MagicMock()
    assert is_retryable_error(RateLimitError(message="Rate limit", response=mock_response, body=None)) is False


def test_is_retryable_error_transient_5xx() -> None:
    """Test that transient 5xx errors are retryable."""
    mock_request = MagicMock()
    error_500 = APIError(message="Internal error", request=mock_request, body=None)
    error_500.status_code = 500
    assert is_retryable_error(error_500) is True

    error_502 = APIError(message="Bad gateway", request=mock_request, body=None)
    error_502.status_code = 502
    assert is_retryable_error(error_502) is True

    error_503 = APIError(message="Service unavailable", request=mock_request, body=None)
    error_503.status_code = 503
    assert is_retryable_error(error_503) is True

    error_504 = APIError(message="Gateway timeout", request=mock_request, body=None)
    error_504.status_code = 504
    assert is_retryable_error(error_504) is True


def test_is_retryable_error_4xx_not_retryable() -> None:
    """Test that 4xx errors are NOT retryable."""
    mock_request = MagicMock()
    error_400 = APIError(message="Bad request", request=mock_request, body=None)
    error_400.status_code = 400
    assert is_retryable_error(error_400) is False

    error_401 = APIError(message="Unauthorized", request=mock_request, body=None)
    error_401.status_code = 401
    assert is_retryable_error(error_401) is False

    error_403 = APIError(message="Forbidden", request=mock_request, body=None)
    error_403.status_code = 403
    assert is_retryable_error(error_403) is False


def test_is_retryable_error_network_errors() -> None:
    """Test that network errors are retryable."""
    assert is_retryable_error(ConnectionError()) is True
    assert is_retryable_error(OSError()) is True


@pytest.mark.asyncio
async def test_retry_with_backoff_success_first_attempt() -> None:
    """Test retry succeeds on first attempt."""
    func = AsyncMock(return_value="success")
    result = await retry_with_backoff(func)
    assert result == "success"
    assert func.call_count == 1


@pytest.mark.asyncio
async def test_retry_with_backoff_success_after_retry() -> None:
    """Test retry succeeds after one retry."""
    mock_request = MagicMock()
    func = AsyncMock(side_effect=[APITimeoutError(request=mock_request), "success"])
    result = await retry_with_backoff(func, max_retries=2)
    assert result == "success"
    assert func.call_count == 2


@pytest.mark.asyncio
async def test_retry_with_backoff_max_retries_exhausted() -> None:
    """Test retry raises error after max retries."""
    mock_request = MagicMock()
    func = AsyncMock(side_effect=APITimeoutError(request=mock_request))
    with pytest.raises(LLMTimeoutError):
        await retry_with_backoff(func, max_retries=2)
    assert func.call_count == 3  # Initial + 2 retries


@pytest.mark.asyncio
async def test_retry_with_backoff_non_retryable_error() -> None:
    """Test retry does not retry non-retryable errors."""
    mock_request = MagicMock()
    error_400 = APIError(message="Bad request", request=mock_request, body=None)
    error_400.status_code = 400
    func = AsyncMock(side_effect=error_400)

    with pytest.raises(LLMError) as exc_info:
        await retry_with_backoff(func, max_retries=2)

    assert exc_info.value.retryable is False
    assert func.call_count == 1  # No retries


@pytest.mark.asyncio
async def test_retry_with_backoff_rate_limit_error() -> None:
    """Test retry handles rate limit errors correctly."""
    mock_response = MagicMock()
    mock_response.request = MagicMock()
    rate_limit_error = RateLimitError(message="Rate limit", response=mock_response, body=None)
    rate_limit_error.retry_after = 60
    func = AsyncMock(side_effect=rate_limit_error)

    with pytest.raises(LLMRateLimitError) as exc_info:
        await retry_with_backoff(func, max_retries=2)

    assert exc_info.value.retry_after == 60
    assert func.call_count == 1  # No retries for rate limit


@pytest.mark.asyncio
async def test_retry_with_backoff_exponential_backoff() -> None:
    """Test retry uses exponential backoff."""
    mock_request = MagicMock()
    func = AsyncMock(side_effect=[APITimeoutError(request=mock_request), APITimeoutError(request=mock_request), "success"])
    with patch("asyncio.sleep") as mock_sleep:
        result = await retry_with_backoff(func, max_retries=2, base_delay=1.0)

    assert result == "success"
    assert func.call_count == 3
    # Should have slept twice (before retry 1 and retry 2)
    assert mock_sleep.call_count == 2
    # First delay should be ~1s, second should be ~2s (with jitter)
    assert mock_sleep.call_args_list[0][0][0] >= 1.0
    assert mock_sleep.call_args_list[1][0][0] >= 2.0
