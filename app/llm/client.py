"""OpenAI SDK wrapper (provider-agnostic interface)."""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.core.config import settings
from app.core.exceptions import LLMError
from app.llm.prompts import PromptLoader, get_prompt_loader
from app.llm.retry import retry_with_backoff


class LLMClient(ABC):
    """Abstract base class for LLM clients (provider-agnostic interface)."""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """
        Complete a prompt and return the response text.

        Args:
            prompt: The prompt text
            temperature: Temperature for generation (optional)
            max_tokens: Maximum tokens to generate (optional)
            timeout: Request timeout in seconds (optional)

        Returns:
            Generated text response

        Raises:
            LLMError: If the request fails
        """
        pass


class OpenAIClient(LLMClient):
    """OpenAI SDK implementation of LLM client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_concurrent: Optional[int] = None,
        default_timeout: Optional[int] = None,
    ) -> None:
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key (defaults to settings.openai_api_key)
            model: Model to use (defaults to settings.openai_model)
            max_concurrent: Maximum concurrent requests (defaults to settings.llm_max_concurrent_requests)
            default_timeout: Default timeout in seconds (defaults to settings.llm_request_timeout)
        """
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.model = model or settings.openai_model
        self.default_timeout = default_timeout or settings.llm_request_timeout
        self.max_concurrent = max_concurrent or settings.llm_max_concurrent_requests

        # Create OpenAI client
        self._client = AsyncOpenAI(api_key=self.api_key)

        # Semaphore for bounded concurrency
        self._semaphore = asyncio.Semaphore(self.max_concurrent)

        # Prompt loader
        self._prompt_loader = get_prompt_loader()

    async def complete(
        self,
        prompt: str,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """
        Complete a prompt and return the response text.

        Args:
            prompt: The prompt text
            temperature: Temperature for generation (defaults to settings.openai_temperature)
            max_tokens: Maximum tokens to generate (defaults to settings.openai_max_tokens)
            timeout: Request timeout in seconds (defaults to self.default_timeout)

        Returns:
            Generated text response

        Raises:
            LLMError: If the request fails
        """
        temperature = temperature if temperature is not None else settings.openai_temperature
        max_tokens = max_tokens if max_tokens is not None else settings.openai_max_tokens
        timeout = timeout if timeout is not None else self.default_timeout

        async def _make_request() -> ChatCompletion:
            """Make the actual OpenAI API request."""
            async with self._semaphore:  # Bounded concurrency
                try:
                    response = await asyncio.wait_for(
                        self._client.chat.completions.create(
                            model=self.model,
                            messages=[
                                {"role": "user", "content": prompt},
                            ],
                            temperature=temperature,
                            max_tokens=max_tokens,
                        ),
                        timeout=timeout,
                    )
                    return response
                except asyncio.TimeoutError as e:
                    raise asyncio.TimeoutError(
                        f"LLM request timed out after {timeout} seconds"
                    ) from e

        # Use retry logic
        response = await retry_with_backoff(_make_request)

        # Extract text from response
        if not response.choices or not response.choices[0].message.content:
            raise LLMError("Empty response from LLM", retryable=False)

        return response.choices[0].message.content

    async def complete_with_prompt_template(
        self,
        agent_name: str,
        template_vars: Optional[dict[str, str]] = None,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """
        Complete a prompt using a template from prompts directory.

        Args:
            agent_name: Name of the agent (e.g., 'clarifier')
            template_vars: Optional template variables to format the prompt
            temperature: Temperature for generation (optional)
            max_tokens: Maximum tokens to generate (optional)
            timeout: Request timeout in seconds (optional)

        Returns:
            Generated text response

        Raises:
            LLMError: If the request fails
            FileNotFoundError: If prompt template doesn't exist
        """
        # Load prompt template
        prompt_template = self._prompt_loader.load_prompt(agent_name)

        # Format template with variables if provided
        if template_vars:
            prompt = prompt_template.format(**template_vars)
        else:
            prompt = prompt_template

        # Call complete
        return await self.complete(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    async def close(self) -> None:
        """Close the client and cleanup resources."""
        await self._client.close()


# Global client instance
_client: Optional[OpenAIClient] = None


def get_llm_client() -> OpenAIClient:
    """
    Get or create global LLM client instance.

    Returns:
        OpenAIClient instance
    """
    global _client
    if _client is None:
        _client = OpenAIClient()
    return _client


async def close_llm_client() -> None:
    """Close the global LLM client."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None


