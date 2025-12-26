"""Bias Checker Agent implementation."""

import json
from typing import Any

from app.agents.base import Agent
from app.core.exceptions import AgentError, ValidationError
from app.llm.client import get_llm_client
from app.schemas.agents import BiasCheckerInput, BiasCheckerOutput, BiasType
from app.schemas.decision import BiasFinding, Criterion
from app.schemas.state import PipelineState


def validate_bias_type(bias_type: str) -> str:
    """
    Validate that bias_type is one of the allowed values.

    Args:
        bias_type: Bias type string to validate

    Returns:
        Validated bias type string

    Raises:
        ValidationError: If bias_type is not one of the allowed values
    """
    try:
        # Try to match against enum
        BiasType(bias_type)
        return bias_type
    except ValueError:
        # Try case-insensitive match
        bias_type_lower = bias_type.lower()
        for bias_enum in BiasType:
            if bias_enum.value == bias_type_lower:
                return bias_enum.value
        raise ValidationError(
            f"Invalid bias_type: {bias_type}. Must be one of: {[bt.value for bt in BiasType]}"
        )


class BiasChecker(Agent[BiasCheckerOutput]):
    """
    Bias Checker Agent: Detects and names specific cognitive biases.

    This is the third agent in the pipeline. It analyzes the decision context,
    options, and criteria to identify cognitive biases that might influence
    the decision-making process.
    """

    @property
    def name(self) -> str:
        """Return the agent's name."""
        return "bias_checker"

    async def execute(self, state: PipelineState) -> BiasCheckerOutput:
        """
        Execute the Bias Checker Agent.

        Args:
            state: Pipeline state containing normalized_input and criteria_builder_output

        Returns:
            BiasCheckerOutput with bias_findings

        Raises:
            AgentError: If agent execution fails
            ValidationError: If output fails schema validation
        """
        # Extract input from PipelineState
        normalized_input = state.normalized_input
        criteria_builder_output = state.criteria_builder_output

        # Get criteria from criteria_builder_output
        if not criteria_builder_output:
            raise AgentError(
                "Criteria Builder output not found in PipelineState",
                agent_name=self.name,
            )

        try:
            # Build criteria list from criteria_builder_output
            # criteria_builder_output is a dict with "criteria" key containing list of dicts
            criteria_dicts = criteria_builder_output.get("criteria", [])
            criteria_list = [
                Criterion(
                    name=criterion["name"],
                    weight=criterion["weight"],
                    rationale=criterion["rationale"],
                )
                for criterion in criteria_dicts
            ]
        except (KeyError, TypeError) as e:
            raise AgentError(
                f"Failed to extract criteria from criteria_builder_output: {str(e)}",
                agent_name=self.name,
            ) from e

        try:
            # Build BiasCheckerInput
            bias_input = BiasCheckerInput(
                decision_context=normalized_input.get("decision_context", ""),
                options=normalized_input.get("options", []),
                criteria=criteria_list,
            )
        except Exception as e:
            raise AgentError(
                f"Failed to build BiasCheckerInput from PipelineState: {str(e)}",
                agent_name=self.name,
            ) from e

        # Get LLM client
        llm_client = get_llm_client()

        # Prepare prompt data (convert Criterion objects to dicts for JSON)
        criteria_for_prompt = [
            {
                "name": criterion.name,
                "weight": criterion.weight,
                "rationale": criterion.rationale,
            }
            for criterion in criteria_list
        ]
        prompt_data = {
            "decision_context": bias_input.decision_context,
            "options": json.dumps(bias_input.options),
            "criteria": json.dumps(criteria_for_prompt),
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

        # Build bias findings from parsed response
        bias_findings = []
        for finding_dict in parsed_response.get("bias_findings", []):
            try:
                # Validate bias_type
                bias_type = validate_bias_type(finding_dict.get("bias_type", ""))
                # Create BiasFinding with validated bias_type
                bias_finding = BiasFinding(
                    bias_type=bias_type,
                    description=finding_dict.get("description", ""),
                    evidence=finding_dict.get("evidence", ""),
                )
                bias_findings.append(bias_finding)
            except Exception as e:
                raise ValidationError(
                    f"Failed to build BiasFinding: {str(e)}. Finding: {finding_dict}"
                ) from e

        # Validate against BiasCheckerOutput schema
        try:
            output = BiasCheckerOutput(bias_findings=bias_findings)
        except Exception as e:
            raise ValidationError(
                f"BiasCheckerOutput validation failed: {str(e)}"
            ) from e

        return output


