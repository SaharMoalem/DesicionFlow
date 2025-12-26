"""Base agent interface/abstract class."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from app.schemas.state import PipelineState

# Type variable for agent output types (must be Pydantic models)
T = TypeVar("T", bound=BaseModel)


class Agent(ABC, Generic[T]):
    """
    Abstract base class for all agents in the DecisionFlow pipeline.

    All agents must implement the execute method which:
    1. Reads from PipelineState (normalized_input, previous agent outputs)
    2. Calls LLM with prompt template
    3. Parses and validates LLM response
    4. Returns structured output (Pydantic model)
    5. Output is written to PipelineState by the orchestrator

    Agents follow a deterministic execution pattern:
    - Fixed execution order (enforced by orchestrator)
    - Structured inputs/outputs (Pydantic models)
    - Schema validation at every step
    - No side effects (stateless)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the agent's name (e.g., 'clarifier', 'criteria_builder').

        Returns:
            Agent name string
        """
        pass

    @abstractmethod
    async def execute(self, state: PipelineState) -> T:
        """
        Execute the agent's logic and return structured output.

        Args:
            state: Current pipeline state containing:
                - normalized_input (sanitized user input)
                - Previous agent outputs (if any)
                - Version metadata

        Returns:
            Agent-specific output (Pydantic model)

        Raises:
            AgentError: If agent execution fails
            ValidationError: If output fails schema validation
            LLMError: If LLM call fails (after retries)
        """
        pass


