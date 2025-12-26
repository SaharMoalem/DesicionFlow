"""Tests for schema repair mechanism."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import AgentError
from app.validation.repair import repair_schema


@pytest.mark.asyncio
async def test_repair_schema_success() -> None:
    """Test successful schema repair."""
    invalid_json = '{"name": "John", "age": "30"}'  # age should be number
    json_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"},
        },
        "required": ["name", "age"],
    }
    validation_errors = ["age must be a number"]

    # Mock LLM response
    repaired_json_str = '{"name": "John", "age": 30}'

    with patch("app.validation.repair.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=repaired_json_str)
        mock_get_client.return_value = mock_client

        result = await repair_schema(
            invalid_json=invalid_json,
            json_schema=json_schema,
            validation_errors=validation_errors,
        )

        assert result == {"name": "John", "age": 30}
        mock_client.complete_with_prompt_template.assert_called_once()


@pytest.mark.asyncio
async def test_repair_schema_markdown_json() -> None:
    """Test repair handles markdown-wrapped JSON."""
    invalid_json = '{"name": "John"}'
    json_schema = {"type": "object"}
    validation_errors = []

    # Mock LLM response with markdown
    repaired_json_str = "```json\n{\"name\": \"John\", \"age\": 30}\n```"

    with patch("app.validation.repair.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=repaired_json_str)
        mock_get_client.return_value = mock_client

        result = await repair_schema(
            invalid_json=invalid_json,
            json_schema=json_schema,
            validation_errors=validation_errors,
        )

        assert result == {"name": "John", "age": 30}


@pytest.mark.asyncio
async def test_repair_schema_invalid_json_response() -> None:
    """Test repair fails when LLM returns invalid JSON."""
    invalid_json = '{"name": "John"}'
    json_schema = {"type": "object"}
    validation_errors = []

    # Mock LLM response with invalid JSON
    repaired_json_str = "This is not JSON"

    with patch("app.validation.repair.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=repaired_json_str)
        mock_get_client.return_value = mock_client

        with pytest.raises(AgentError) as exc_info:
            await repair_schema(
                invalid_json=invalid_json,
                json_schema=json_schema,
                validation_errors=validation_errors,
            )

        assert "not valid JSON" in str(exc_info.value)
        assert exc_info.value.agent_name == "repair"


@pytest.mark.asyncio
async def test_repair_schema_llm_error() -> None:
    """Test repair fails when LLM call fails."""
    invalid_json = '{"name": "John"}'
    json_schema = {"type": "object"}
    validation_errors = []

    with patch("app.validation.repair.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(
            side_effect=Exception("LLM error")
        )
        mock_get_client.return_value = mock_client

        with pytest.raises(AgentError) as exc_info:
            await repair_schema(
                invalid_json=invalid_json,
                json_schema=json_schema,
                validation_errors=validation_errors,
            )

        assert "LLM call failed" in str(exc_info.value)
        assert exc_info.value.agent_name == "repair"


@pytest.mark.asyncio
async def test_repair_schema_with_agent_name() -> None:
    """Test repair includes agent name in prompt."""
    invalid_json = '{"name": "John"}'
    json_schema = {"type": "object"}
    validation_errors = []
    agent_name = "clarifier"

    repaired_json_str = '{"name": "John", "age": 30}'

    with patch("app.validation.repair.get_llm_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.complete_with_prompt_template = AsyncMock(return_value=repaired_json_str)
        mock_get_client.return_value = mock_client

        await repair_schema(
            invalid_json=invalid_json,
            json_schema=json_schema,
            validation_errors=validation_errors,
            agent_name=agent_name,
        )

        # Verify agent_name was passed to prompt template vars
        call_args = mock_client.complete_with_prompt_template.call_args
        assert call_args[1]["template_vars"]["agent_name"] == agent_name
