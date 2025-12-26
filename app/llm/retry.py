"""Retry logic with exponential backoff and jitter."""

import asyncio
import random
from typing import Callable, TypeVar

from openai import APIError, APITimeoutError, RateLimitError

from app.core.exceptions import LLMError, LLMRateLimitError, LLMTimeoutError

T = TypeVar("T")


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is retryable.

    Retryable errors:
    - Timeouts
    - Transient 5xx errors (500, 502, 503, 504)
    - Network errors

    Non-retryable errors:
    - 4xx errors (client errors)
    - 429 (rate limit) - handled separately
    - Authentication errors (401, 403)
    - Business logic errors

    Args:
        error: The exception to check

    Returns:
        True if the error is retryable, False otherwise
    """
    # Timeouts are retryable
    if isinstance(error, (APITimeoutError, TimeoutError, asyncio.TimeoutError)):
        return True

    # Rate limit errors are NOT retryable (handled separately)
    if isinstance(error, RateLimitError):
        return False

    # OpenAI API errors
    if isinstance(error, APIError):
        status_code = getattr(error, "status_code", None)
        if status_code is None:
            # Network errors or unknown errors - retry
            return True

        # Transient 5xx errors are retryable
        if status_code in (500, 502, 503, 504):
            return True

        # 4xx errors are NOT retryable (client errors)
        if 400 <= status_code < 500:
            return False

        # Other 5xx errors - retry
        if 500 <= status_code < 600:
            return True

    # Network errors (connection errors, etc.) are retryable
    if isinstance(error, (ConnectionError, OSError)):
        return True

    # Unknown errors - don't retry (fail fast)
    return False


async def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 2,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
) -> T:
    """
    Retry a function with exponential backoff and jitter.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retries (default: 2, so 3 total attempts)
        base_delay: Base delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 10.0)

    Returns:
        Result of the function call

    Raises:
        LLMError: If all retries are exhausted
        LLMTimeoutError: If timeout occurs
        LLMRateLimitError: If rate limit is exceeded
    """
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):  # 0, 1, 2 = 3 attempts total
        try:
            return await func()
        except Exception as e:
            last_error = e

            # Check if this is the last attempt
            if attempt >= max_retries:
                break

            # Check if error is retryable
            if not is_retryable_error(e):
                # Non-retryable error - raise immediately
                if isinstance(e, RateLimitError):
                    # Check if this is a quota error vs rate limit error
                    # OpenAI returns 429 for both rate limits and quota issues
                    # We distinguish by checking the error message/code
                    error_message = str(e).lower()
                    error_code = getattr(e, "code", None) or getattr(e, "response", {}).get("body", {}).get("error", {}).get("code") if hasattr(e, "response") else None
                    
                    if error_code == "insufficient_quota" or "quota" in error_message or "billing" in error_message or "insufficient_quota" in error_message:
                        # This is a quota/billing issue, not a rate limit
                        raise LLMError(
                            f"OpenAI quota exceeded. Please check your billing and plan details at https://platform.openai.com/account/billing. Error: {str(e)}",
                            retryable=False,
                            status_code=429,
                            original_error=e,
                        ) from e
                    
                    retry_after = getattr(e, "retry_after", None)
                    raise LLMRateLimitError(
                        f"Rate limit exceeded: {str(e)}", retry_after=retry_after
                    ) from e
                raise LLMError(
                    f"Non-retryable error: {str(e)}",
                    retryable=False,
                    original_error=e,
                ) from e

            # Calculate delay with exponential backoff and jitter
            delay = min(base_delay * (2**attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)  # 10% jitter
            total_delay = delay + jitter

            # Wait before retrying
            await asyncio.sleep(total_delay)

    # All retries exhausted
    if isinstance(last_error, (APITimeoutError, TimeoutError, asyncio.TimeoutError)):
        raise LLMTimeoutError(f"Request timed out after {max_retries + 1} attempts") from last_error

    if isinstance(last_error, RateLimitError):
        # Check if this is a quota error vs rate limit error
        error_message = str(last_error).lower()
        error_code = getattr(last_error, "code", None) or (getattr(last_error, "response", {}).get("body", {}).get("error", {}).get("code") if hasattr(last_error, "response") else None)
        
        if error_code == "insufficient_quota" or "quota" in error_message or "billing" in error_message or "insufficient_quota" in error_message:
            # This is a quota/billing issue, not a rate limit
            raise LLMError(
                f"OpenAI quota exceeded. Please check your billing and plan details at https://platform.openai.com/account/billing. Error: {str(last_error)}",
                retryable=False,
                status_code=429,
                original_error=last_error,
            ) from last_error
        
        retry_after = getattr(last_error, "retry_after", None)
        raise LLMRateLimitError(
            f"Rate limit exceeded: {str(last_error)}", retry_after=retry_after
        ) from last_error

    # Generic LLM error
    status_code = getattr(last_error, "status_code", None) if hasattr(last_error, "status_code") else None
    
    # Check for quota errors in APIError as well (429 status)
    if isinstance(last_error, APIError) and status_code == 429:
        error_message = str(last_error).lower()
        error_code = getattr(last_error, "code", None) or (getattr(last_error, "response", {}).get("body", {}).get("error", {}).get("code") if hasattr(last_error, "response") else None)
        
        if error_code == "insufficient_quota" or "quota" in error_message or "billing" in error_message or "insufficient_quota" in error_message:
            raise LLMError(
                f"OpenAI quota exceeded. Please check your billing and plan details at https://platform.openai.com/account/billing. Error: {str(last_error)}",
                retryable=False,
                status_code=429,
                original_error=last_error,
            ) from last_error
    
    raise LLMError(
        f"LLM request failed after {max_retries + 1} attempts: {str(last_error)}",
        retryable=True,
        status_code=status_code,
        original_error=last_error,
    ) from last_error


