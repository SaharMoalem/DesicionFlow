"""Decision Synthesizer Agent implementation."""

import json
from typing import Any

from app.agents.base import Agent
from app.core.exceptions import AgentError, ValidationError
from app.llm.client import get_llm_client
from app.schemas.agents import DecisionSynthesizerInput, DecisionSynthesizerOutput
from app.schemas.decision import BiasFinding, Criterion, OptionScores
from app.schemas.state import PipelineState


class DecisionSynthesizer(Agent[DecisionSynthesizerOutput]):
    """
    Decision Synthesizer Agent: Produces final recommendation with confidence score.

    This is the final agent in the pipeline. It synthesizes all previous agent
    outputs (criteria, scores, biases) into a clear, defensible recommendation
    with confidence scoring and explicit trade-offs.
    """

    @property
    def name(self) -> str:
        """Return the agent's name."""
        return "decision_synthesizer"

    async def execute(self, state: PipelineState) -> DecisionSynthesizerOutput:
        """
        Execute the Decision Synthesizer Agent.

        Args:
            state: Pipeline state containing all previous agent outputs

        Returns:
            DecisionSynthesizerOutput with winner, confidence, trade-offs, etc.

        Raises:
            AgentError: If agent execution fails
            ValidationError: If output fails schema validation
        """
        # Extract input from PipelineState
        normalized_input = state.normalized_input
        criteria_builder_output = state.criteria_builder_output
        bias_checker_output = state.bias_checker_output
        option_evaluator_output = state.option_evaluator_output

        # Validate that all required outputs are present
        if not criteria_builder_output:
            raise AgentError(
                "Criteria Builder output not found in PipelineState",
                agent_name=self.name,
            )
        if not option_evaluator_output:
            raise AgentError(
                "Option Evaluator output not found in PipelineState",
                agent_name=self.name,
            )

        try:
            # Build criteria list from criteria_builder_output
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
            # Build scores dict from option_evaluator_output
            scores_dict = option_evaluator_output.get("scores", {})
            # Convert dict values to OptionScores objects
            option_scores_dict: dict[str, OptionScores] = {}
            for option_name, scores_data in scores_dict.items():
                option_scores_dict[option_name] = OptionScores(**scores_data)
        except Exception as e:
            raise AgentError(
                f"Failed to extract scores from option_evaluator_output: {str(e)}",
                agent_name=self.name,
            ) from e

        try:
            # Build bias findings list from bias_checker_output
            bias_findings_list = []
            if bias_checker_output:
                for finding_dict in bias_checker_output.get("bias_findings", []):
                    bias_findings_list.append(BiasFinding(**finding_dict))
        except Exception as e:
            raise AgentError(
                f"Failed to extract bias findings from bias_checker_output: {str(e)}",
                agent_name=self.name,
            ) from e

        try:
            # Build DecisionSynthesizerInput
            synthesizer_input = DecisionSynthesizerInput(
                decision_context=normalized_input.get("decision_context", ""),
                options=normalized_input.get("options", []),
                criteria=criteria_list,
                scores=option_scores_dict,
                bias_findings=bias_findings_list,
            )
        except Exception as e:
            raise AgentError(
                f"Failed to build DecisionSynthesizerInput from PipelineState: {str(e)}",
                agent_name=self.name,
            ) from e

        # Get LLM client
        llm_client = get_llm_client()

        # Prepare prompt data
        criteria_for_prompt = [
            {
                "name": criterion.name,
                "weight": criterion.weight,
                "rationale": criterion.rationale,
            }
            for criterion in criteria_list
        ]

        scores_for_prompt = {}
        for option_name, option_scores in option_scores_dict.items():
            scores_for_prompt[option_name] = {
                "total_score": option_scores.total_score,
                "breakdown": [
                    {
                        "criterion_name": score.criterion_name,
                        "score": score.score,
                        "justification": score.justification,
                    }
                    for score in option_scores.breakdown
                ],
            }

        bias_findings_for_prompt = [
            {
                "bias_type": finding.bias_type,
                "description": finding.description,
                "evidence": finding.evidence,
            }
            for finding in bias_findings_list
        ]

        prompt_data = {
            "decision_context": synthesizer_input.decision_context,
            "options": json.dumps(synthesizer_input.options),
            "criteria": json.dumps(criteria_for_prompt),
            "scores": json.dumps(scores_for_prompt),
            "bias_findings": json.dumps(bias_findings_for_prompt),
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

        # Validate winner is one of the options
        winner = parsed_response.get("winner", "")
        if winner not in synthesizer_input.options:
            raise ValidationError(
                f"Winner '{winner}' is not one of the options: {synthesizer_input.options}"
            )

        # Validate confidence score
        confidence = parsed_response.get("confidence", 0.0)
        if not (0.0 <= confidence <= 1.0):
            raise ValidationError(f"Confidence score {confidence} must be between 0.0 and 1.0")

        # Validate confidence breakdown
        confidence_breakdown_dict = parsed_response.get("confidence_breakdown", {})
        for key in ["input_completeness", "agent_agreement", "evidence_strength", "bias_impact"]:
            if key not in confidence_breakdown_dict:
                raise ValidationError(f"Missing confidence breakdown factor: {key}")
            value = confidence_breakdown_dict[key]
            if not (0.0 <= value <= 1.0):
                raise ValidationError(
                    f"Confidence breakdown factor {key} ({value}) must be between 0.0 and 1.0"
                )

        # Validate against DecisionSynthesizerOutput schema
        try:
            output = DecisionSynthesizerOutput(**parsed_response)
        except Exception as e:
            raise ValidationError(
                f"DecisionSynthesizerOutput validation failed: {str(e)}"
            ) from e

        return output


