"""Criteria Builder Agent implementation."""

import json
from typing import Any

from app.agents.base import Agent
from app.core.exceptions import AgentError, ValidationError
from app.llm.client import get_llm_client
from app.schemas.agents import CriteriaBuilderInput, CriteriaBuilderOutput
from app.schemas.decision import Criterion
from app.schemas.state import PipelineState


def normalize_weights(criteria: list[Criterion]) -> list[Criterion]:
    """
    Normalize criterion weights to sum to 1.0.

    Args:
        criteria: List of criteria with weights

    Returns:
        List of criteria with normalized weights

    Raises:
        ValueError: If all weights are zero or criteria list is empty
    """
    if not criteria:
        raise ValueError("Cannot normalize weights: criteria list is empty")

    total_weight = sum(criterion.weight for criterion in criteria)

    if total_weight == 0.0:
        # If all weights are zero, distribute equally
        equal_weight = 1.0 / len(criteria)
        return [
            Criterion(name=criterion.name, weight=equal_weight, rationale=criterion.rationale)
            for criterion in criteria
        ]

    # Normalize proportionally
    return [
        Criterion(
            name=criterion.name,
            weight=criterion.weight / total_weight,
            rationale=criterion.rationale,
        )
        for criterion in criteria
    ]


class CriteriaBuilder(Agent[CriteriaBuilderOutput]):
    """
    Criteria Builder Agent: Converts vague goals into weighted evaluation criteria.

    This is the second agent in the pipeline. It analyzes the decision context
    and options to generate a set of weighted evaluation criteria that will be
    used to score each option.
    """

    @property
    def name(self) -> str:
        """Return the agent's name."""
        return "criteria_builder"

    async def execute(self, state: PipelineState) -> CriteriaBuilderOutput:
        """
        Execute the Criteria Builder Agent.

        Args:
            state: Pipeline state containing normalized_input

        Returns:
            CriteriaBuilderOutput with criteria (weights normalized to sum to 1.0)

        Raises:
            AgentError: If agent execution fails
            ValidationError: If output fails schema validation
        """
        # Extract input from PipelineState
        normalized_input = state.normalized_input

        try:
            # Build CriteriaBuilderInput from normalized_input
            criteria_input = CriteriaBuilderInput(
                decision_context=normalized_input.get("decision_context", ""),
                options=normalized_input.get("options", []),
                constraints=normalized_input.get("constraints"),
                criteria_preferences=normalized_input.get("criteria_preferences"),
            )
        except Exception as e:
            raise AgentError(
                f"Failed to build CriteriaBuilderInput from PipelineState: {str(e)}",
                agent_name=self.name,
            ) from e

        # Get LLM client
        llm_client = get_llm_client()

        # Prepare prompt data
        prompt_data = {
            "decision_context": criteria_input.decision_context,
            "options": json.dumps(criteria_input.options),
            "constraints": json.dumps(criteria_input.constraints) if criteria_input.constraints else "None",
            "criteria_preferences": (
                json.dumps(criteria_input.criteria_preferences)
                if criteria_input.criteria_preferences
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

        # Build criteria from parsed response
        try:
            criteria_list = [
                Criterion(**criterion_dict) for criterion_dict in parsed_response.get("criteria", [])
            ]
        except Exception as e:
            raise ValidationError(
                f"Failed to build Criterion objects: {str(e)}. Parsed: {parsed_response}"
            ) from e

        # Normalize weights to sum to 1.0
        try:
            normalized_criteria = normalize_weights(criteria_list)
        except ValueError as e:
            raise ValidationError(f"Weight normalization failed: {str(e)}") from e

        # Validate against CriteriaBuilderOutput schema
        try:
            output = CriteriaBuilderOutput(criteria=normalized_criteria)
        except Exception as e:
            raise ValidationError(
                f"CriteriaBuilderOutput validation failed: {str(e)}"
            ) from e

        # Verify weights sum to 1.0 (with small tolerance for floating point)
        total_weight = sum(criterion.weight for criterion in output.criteria)
        if abs(total_weight - 1.0) > 0.001:
            raise ValidationError(
                f"Weights do not sum to 1.0 after normalization: {total_weight}"
            )

        return output


