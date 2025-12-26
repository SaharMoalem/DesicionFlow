"""Tests for LLM client."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from openai import APIError, APITimeoutError
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

from app.core.config import settings
from app.core.exceptions import LLMError, LLMTimeoutError
from app.llm.client import OpenAIClient, get_llm_client
from app.llm.prompts import PromptLoader


@pytest.fixture
def mock_openai_client() -> AsyncMock:
    """Create a mock OpenAI client."""
    from openai.types.completion_usage import CompletionUsage
    
    mock_client = AsyncMock()
    mock_response = ChatCompletion(
        id="test-id",
        object="chat.completion",
        created=1234567890,
        model="gpt-4",
        choices=[
            Choice(
                index=0,
                message=ChatCompletionMessage(
                    role="assistant", content="Test response"
                ),
                finish_reason="stop",
            )
        ],
        usage=CompletionUsage(completion_tokens=10, prompt_tokens=5, total_tokens=15),
    )
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    return mock_client


@pytest.fixture
def llm_client(mock_openai_client: AsyncMock) -> OpenAIClient:
    """Create LLM client with mocked OpenAI client."""
    with patch("app.llm.client.AsyncOpenAI", return_value=mock_openai_client):
        client = OpenAIClient(api_key="test-key", model="gpt-4")
        client._client = mock_openai_client
        return client


@pytest.mark.asyncio
async def test_openai_client_complete_success(llm_client: OpenAIClient) -> None:
    """Test OpenAI client completes successfully."""
    response = await llm_client.complete("Test prompt")
    assert response == "Test response"
    llm_client._client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_openai_client_complete_with_custom_params(
    llm_client: OpenAIClient,
) -> None:
    """Test OpenAI client with custom temperature and max_tokens."""
    await llm_client.complete(
        "Test prompt", temperature=0.5, max_tokens=1000, timeout=60
    )

    call_args = llm_client._client.chat.completions.create.call_args
    assert call_args.kwargs["temperature"] == 0.5
    assert call_args.kwargs["max_tokens"] == 1000


@pytest.mark.asyncio
async def test_openai_client_complete_timeout(llm_client: OpenAIClient) -> None:
    """Test OpenAI client handles timeout."""
    llm_client._client.chat.completions.create = AsyncMock(
        side_effect=asyncio.TimeoutError("Request timed out")
    )

    with pytest.raises(LLMTimeoutError):
        await llm_client.complete("Test prompt", timeout=5)


@pytest.mark.asyncio
async def test_openai_client_complete_empty_response(
    llm_client: OpenAIClient,
) -> None:
    """Test OpenAI client handles empty response."""
    from openai.types.completion_usage import CompletionUsage
    
    # Create response with None content (simulating empty response)
    empty_response = ChatCompletion(
        id="test-id",
        object="chat.completion",
        created=1234567890,
        model="gpt-4",
        choices=[
            Choice(
                index=0,
                message=ChatCompletionMessage(role="assistant", content=None),
                finish_reason="stop",
            )
        ],
        usage=CompletionUsage(completion_tokens=10, prompt_tokens=5, total_tokens=15),
    )
    llm_client._client.chat.completions.create = AsyncMock(return_value=empty_response)

    with pytest.raises(LLMError) as exc_info:
        await llm_client.complete("Test prompt")

    assert "Empty response" in str(exc_info.value)
    assert exc_info.value.retryable is False


@pytest.mark.asyncio
async def test_openai_client_bounded_concurrency(llm_client: OpenAIClient) -> None:
    """Test OpenAI client enforces bounded concurrency."""
    # Create client with max_concurrent=2
    client = OpenAIClient(api_key="test-key", max_concurrent=2)
    client._client = llm_client._client

    # Track concurrent calls
    concurrent_calls = 0
    max_concurrent = 0

    async def track_concurrency(*args, **kwargs):
        nonlocal concurrent_calls, max_concurrent
        concurrent_calls += 1
        max_concurrent = max(max_concurrent, concurrent_calls)
        await asyncio.sleep(0.1)  # Simulate work
        concurrent_calls -= 1
        return llm_client._client.chat.completions.create.return_value

    client._client.chat.completions.create = AsyncMock(side_effect=track_concurrency)

    # Make 5 concurrent requests
    tasks = [client.complete(f"Prompt {i}") for i in range(5)]
    await asyncio.gather(*tasks)

    # Should never exceed max_concurrent (2)
    assert max_concurrent <= 2


@pytest.mark.asyncio
async def test_openai_client_complete_with_prompt_template(
    llm_client: OpenAIClient,
) -> None:
    """Test OpenAI client with prompt template."""
    # Mock prompt loader
    with patch.object(llm_client._prompt_loader, "load_prompt", return_value="Template: {var}"):
        response = await llm_client.complete_with_prompt_template(
            "clarifier", template_vars={"var": "value"}
        )

    assert response == "Test response"
    # Verify the prompt was formatted
    call_args = llm_client._client.chat.completions.create.call_args
    assert "Template: value" in call_args.kwargs["messages"][0]["content"]


@pytest.mark.asyncio
async def test_openai_client_close(llm_client: OpenAIClient) -> None:
    """Test OpenAI client can be closed."""
    await llm_client.close()
    llm_client._client.close.assert_called_once()


def test_openai_client_requires_api_key() -> None:
    """Test OpenAI client requires API key."""
    with patch.dict("os.environ", {}, clear=True):
        with patch("app.llm.client.settings") as mock_settings:
            mock_settings.openai_api_key = ""
            with pytest.raises(ValueError, match="API key is required"):
                OpenAIClient()


def test_get_llm_client_returns_singleton() -> None:
    """Test get_llm_client returns same instance."""
    with patch("app.llm.client.OpenAIClient") as mock_client_class:
        mock_client_class.return_value = MagicMock()
        client1 = get_llm_client()
        client2 = get_llm_client()
        assert client1 is client2
