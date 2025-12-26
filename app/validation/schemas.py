"""JSON Schema definitions for repair."""

from typing import Any

from pydantic import BaseModel


def get_json_schema(model: type[BaseModel]) -> dict[str, Any]:
    """
    Get JSON Schema for a Pydantic model.

    Args:
        model: Pydantic model class

    Returns:
        JSON Schema dictionary
    """
    return model.model_json_schema(mode="serialization")


def get_json_schema_for_agent_output(agent_name: str) -> dict[str, Any]:
    """
    Get JSON Schema for an agent's output model.

    Args:
        agent_name: Name of the agent (e.g., 'clarifier', 'criteria_builder')

    Returns:
        JSON Schema dictionary

    Raises:
        ValueError: If agent_name is not recognized
    """
    from app.schemas.agents import (
        BiasCheckerOutput,
        ClarifierOutput,
        CriteriaBuilderOutput,
        DecisionSynthesizerOutput,
        OptionEvaluatorOutput,
    )

    schema_map = {
        "clarifier": ClarifierOutput,
        "criteria_builder": CriteriaBuilderOutput,
        "bias_checker": BiasCheckerOutput,
        "option_evaluator": OptionEvaluatorOutput,
        "decision_synthesizer": DecisionSynthesizerOutput,
    }

    if agent_name not in schema_map:
        raise ValueError(f"Unknown agent name: {agent_name}")

    return get_json_schema(schema_map[agent_name])


def get_json_schema_for_request() -> dict[str, Any]:
    """
    Get JSON Schema for DecisionRequest.

    Returns:
        JSON Schema dictionary
    """
    from app.schemas.decision import DecisionRequest

    return get_json_schema(DecisionRequest)


def get_json_schema_for_response() -> dict[str, Any]:
    """
    Get JSON Schema for DecisionResponse.

    Returns:
        JSON Schema dictionary
    """
    from app.schemas.decision import DecisionResponse

    return get_json_schema(DecisionResponse)


