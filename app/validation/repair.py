"""Schema repair mechanism."""

import json
from typing import Any

from app.core.exceptions import AgentError
from app.llm.client import get_llm_client


async def repair_schema(
    invalid_json: str,
    json_schema: dict[str, Any],
    validation_errors: list[str],
    agent_name: str | None = None,
) -> dict[str, Any]:
    """
    Attempt to repair invalid JSON using LLM.

    This is a one-shot repair attempt. If repair fails, the caller should
    return SCHEMA_VALIDATION_FAILED error.

    Args:
        invalid_json: The invalid JSON string
        json_schema: JSON Schema that the output should conform to
        validation_errors: List of validation error messages
        agent_name: Optional agent name for context

    Returns:
        Repaired JSON as dictionary

    Raises:
        AgentError: If repair fails
    """
    llm_client = get_llm_client()

    # Prepare prompt data
    template_vars = {
        "invalid_json": invalid_json[:2000],  # Limit size
        "json_schema": json.dumps(json_schema, indent=2),
        "validation_errors": json.dumps(validation_errors),
        "agent_name": agent_name or "unknown",
    }

    try:
        # Call LLM with repair prompt
        # agent_name="repair" is the prompt template name
        llm_response = await llm_client.complete_with_prompt_template(
            agent_name="repair",
            template_vars=template_vars,
        )
    except Exception as e:
        raise AgentError(
            f"Schema repair LLM call failed: {str(e)}",
            agent_name="repair",
        ) from e

    # Parse LLM response as JSON
    try:
        # Try to extract JSON from response (handle markdown code blocks)
        response_text = llm_response.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()

        repaired_json = json.loads(response_text)
        return repaired_json
    except json.JSONDecodeError as e:
        raise AgentError(
            f"Schema repair failed: LLM response is not valid JSON. {str(e)}",
            agent_name="repair",
        ) from e


