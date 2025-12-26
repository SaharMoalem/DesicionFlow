"""Centralized validation service."""

import json
from typing import Any

from pydantic import BaseModel, ValidationError

from app.core.exceptions import ValidationError as AppValidationError
from app.schemas.errors import ErrorCode
from app.validation.repair import repair_schema
from app.validation.schemas import (
    get_json_schema,
    get_json_schema_for_agent_output,
    get_json_schema_for_request,
    get_json_schema_for_response,
)


class ValidationResult:
    """Result of validation operation."""

    def __init__(
        self,
        is_valid: bool,
        data: Any | None = None,
        errors: list[str] | None = None,
    ) -> None:
        self.is_valid = is_valid
        self.data = data
        self.errors = errors or []


async def validate_request(
    request_data: dict[str, Any], attempt_repair: bool = True
) -> ValidationResult:
    """
    Validate request payload against DecisionRequest schema.

    Args:
        request_data: Request data to validate
        attempt_repair: Whether to attempt schema repair if validation fails

    Returns:
        ValidationResult
    """
    from app.schemas.decision import DecisionRequest

    try:
        # Validate against DecisionRequest schema
        request = DecisionRequest(**request_data)
        return ValidationResult(is_valid=True, data=request)
    except ValidationError as e:
        # Extract validation errors
        errors = [str(err) for err in e.errors()]

        # Attempt repair if enabled
        if attempt_repair:
            try:
                json_schema = get_json_schema_for_request()
                invalid_json = json.dumps(request_data) if isinstance(request_data, dict) else str(request_data)
                repaired_data = await repair_schema(
                    invalid_json=invalid_json,
                    json_schema=json_schema,
                    validation_errors=errors,
                )

                # Try validation again with repaired data
                try:
                    request = DecisionRequest(**repaired_data)
                    return ValidationResult(is_valid=True, data=request)
                except ValidationError:
                    # Repair failed, return error
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"Schema validation failed after repair attempt: {errors}"],
                    )
            except Exception:
                # Repair attempt failed
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Schema validation failed and repair failed: {errors}"],
                )

        return ValidationResult(is_valid=False, errors=errors)


async def validate_agent_output(
    agent_name: str,
    output_data: dict[str, Any],
    attempt_repair: bool = True,
) -> ValidationResult:
    """
    Validate agent output against agent-specific output schema.

    Args:
        agent_name: Name of the agent (e.g., 'clarifier', 'criteria_builder')
        output_data: Agent output data to validate
        attempt_repair: Whether to attempt schema repair if validation fails

    Returns:
        ValidationResult
    """
    # Get the appropriate output model
    from app.schemas.agents import (
        BiasCheckerOutput,
        ClarifierOutput,
        CriteriaBuilderOutput,
        DecisionSynthesizerOutput,
        OptionEvaluatorOutput,
    )

    model_map = {
        "clarifier": ClarifierOutput,
        "criteria_builder": CriteriaBuilderOutput,
        "bias_checker": BiasCheckerOutput,
        "option_evaluator": OptionEvaluatorOutput,
        "decision_synthesizer": DecisionSynthesizerOutput,
    }

    if agent_name not in model_map:
        return ValidationResult(
            is_valid=False,
            errors=[f"Unknown agent name: {agent_name}"],
        )

    output_model = model_map[agent_name]

    try:
        # Validate against agent output schema
        output = output_model(**output_data)
        return ValidationResult(is_valid=True, data=output)
    except ValidationError as e:
        # Extract validation errors
        errors = [str(err) for err in e.errors()]

        # Attempt repair if enabled
        if attempt_repair:
            try:
                json_schema = get_json_schema_for_agent_output(agent_name)
                invalid_json = json.dumps(output_data) if isinstance(output_data, dict) else str(output_data)
                repaired_data = await repair_schema(
                    invalid_json=invalid_json,
                    json_schema=json_schema,
                    validation_errors=errors,
                    agent_name=agent_name,
                )

                # Try validation again with repaired data
                try:
                    output = output_model(**repaired_data)
                    return ValidationResult(is_valid=True, data=output)
                except ValidationError:
                    # Repair failed, return error
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"Schema validation failed after repair attempt: {errors}"],
                    )
            except Exception:
                # Repair attempt failed
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Schema validation failed and repair failed: {errors}"],
                )

        return ValidationResult(is_valid=False, errors=errors)


async def validate_response(
    response_data: dict[str, Any], attempt_repair: bool = True
) -> ValidationResult:
    """
    Validate response payload against DecisionResponse schema.

    Args:
        response_data: Response data to validate
        attempt_repair: Whether to attempt schema repair if validation fails

    Returns:
        ValidationResult
    """
    from app.schemas.decision import DecisionResponse

    try:
        # Validate against DecisionResponse schema
        response = DecisionResponse(**response_data)
        return ValidationResult(is_valid=True, data=response)
    except ValidationError as e:
        # Extract validation errors
        errors = [str(err) for err in e.errors()]

        # Attempt repair if enabled
        if attempt_repair:
            try:
                json_schema = get_json_schema_for_response()
                invalid_json = json.dumps(response_data) if isinstance(response_data, dict) else str(response_data)
                repaired_data = await repair_schema(
                    invalid_json=invalid_json,
                    json_schema=json_schema,
                    validation_errors=errors,
                )

                # Try validation again with repaired data
                try:
                    response = DecisionResponse(**repaired_data)
                    return ValidationResult(is_valid=True, data=response)
                except ValidationError:
                    # Repair failed, return error
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"Schema validation failed after repair attempt: {errors}"],
                    )
            except Exception:
                # Repair attempt failed
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Schema validation failed and repair failed: {errors}"],
                )

        return ValidationResult(is_valid=False, errors=errors)


