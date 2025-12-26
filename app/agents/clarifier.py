"""Clarifier Agent implementation."""

import json
from typing import Any

from app.agents.base import Agent
from app.core.exceptions import AgentError, ValidationError
from app.llm.client import get_llm_client
from app.schemas.agents import ClarifierInput, ClarifierOutput
from app.schemas.state import PipelineState


class Clarifier(Agent[ClarifierOutput]):
    """
    Clarifier Agent: Identifies missing inputs and asks essential questions.

    This is the first agent in the pipeline. It analyzes the decision request
    and identifies any missing required information, returning structured
    questions to gather the necessary context.
    """

    @property
    def name(self) -> str:
        """Return the agent's name."""
        return "clarifier"

    async def execute(self, state: PipelineState) -> ClarifierOutput:
        """
        Execute the Clarifier Agent.

        Args:
            state: Pipeline state containing normalized_input

        Returns:
            ClarifierOutput with missing_fields and questions

        Raises:
            AgentError: If agent execution fails
            ValidationError: If output fails schema validation
        """
        # Extract input from PipelineState
        normalized_input = state.normalized_input

        try:
            # Build ClarifierInput from normalized_input
            clarifier_input = ClarifierInput(
                decision_context=normalized_input.get("decision_context", ""),
                options=normalized_input.get("options", []),
                constraints=normalized_input.get("constraints"),
                criteria_preferences=normalized_input.get("criteria_preferences"),
                context_metadata=normalized_input.get("context_metadata"),
            )
        except Exception as e:
            raise AgentError(
                f"Failed to build ClarifierInput from PipelineState: {str(e)}",
                agent_name=self.name,
            ) from e

        # Get LLM client
        llm_client = get_llm_client()

        # Prepare prompt data
        prompt_data = {
            "decision_context": clarifier_input.decision_context,
            "options": json.dumps(clarifier_input.options),
            "constraints": json.dumps(clarifier_input.constraints) if clarifier_input.constraints else "None",
            "criteria_preferences": (
                json.dumps(clarifier_input.criteria_preferences)
                if clarifier_input.criteria_preferences
                else "None"
            ),
        }

        try:
            # Call LLM with prompt template
            llm_response = await llm_client.complete_with_prompt_template(
                agent_name=self.name,
                template_vars=prompt_data,
            )
        except Exception as e:
            raise AgentError(
                f"LLM call failed: {str(e)}",
                agent_name=self.name,
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

            parsed_response = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise AgentError(
                f"Failed to parse LLM response as JSON: {str(e)}. Response: {llm_response[:200]}",
                agent_name=self.name,
            ) from e

        # Validate against ClarifierOutput schema
        try:
            output = ClarifierOutput(**parsed_response)
        except Exception as e:
            raise ValidationError(
                f"ClarifierOutput validation failed: {str(e)}. Parsed: {parsed_response}"
            ) from e

        return output


