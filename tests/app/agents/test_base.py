"""Tests for base agent interface."""

import pytest
from abc import ABC

from app.agents.base import Agent
from app.schemas.state import PipelineState
from pydantic import BaseModel


class MockAgentOutput(BaseModel):
    """Mock output model for agent testing."""

    result: str

    model_config = {"extra": "forbid"}


class ConcreteAgent(Agent[MockAgentOutput]):
    """Concrete implementation of Agent for testing."""

    @property
    def name(self) -> str:
        return "test_agent"

    async def execute(self, state: PipelineState) -> MockAgentOutput:
        return MockAgentOutput(result="test_result")


def test_agent_is_abstract_base_class() -> None:
    """Test that Agent is an abstract base class."""
    assert issubclass(Agent, ABC)


def test_agent_cannot_be_instantiated() -> None:
    """Test that Agent abstract class cannot be instantiated."""
    with pytest.raises(TypeError):
        Agent()  # type: ignore


def test_concrete_agent_can_be_instantiated() -> None:
    """Test that concrete agent implementation can be instantiated."""
    agent = ConcreteAgent()
    assert agent is not None
    assert agent.name == "test_agent"


@pytest.mark.asyncio
async def test_concrete_agent_execute() -> None:
    """Test that concrete agent execute method works."""
    agent = ConcreteAgent()
    state = PipelineState(
        request_id="test_req",
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
        normalized_input={"test": "data"},
    )

    result = await agent.execute(state)

    assert isinstance(result, MockAgentOutput)
    assert result.result == "test_result"


def test_agent_is_generic() -> None:
    """Test that Agent is a generic type."""
    # This test verifies that Agent[T] type variable works
    agent: Agent[MockAgentOutput] = ConcreteAgent()
    assert agent is not None


def test_agent_name_property() -> None:
    """Test that agent name property is accessible."""
    agent = ConcreteAgent()
    assert isinstance(agent.name, str)
    assert agent.name == "test_agent"

