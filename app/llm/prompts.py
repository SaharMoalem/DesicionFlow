"""Prompt template loading and management."""

import os
from pathlib import Path
from typing import Optional

from app.core.config import settings


class PromptLoader:
    """Loads and caches prompt templates from versioned directories."""

    def __init__(self, logic_version: Optional[str] = None) -> None:
        """
        Initialize prompt loader.

        Args:
            logic_version: Logic version to use (defaults to settings.logic_version)
        """
        self.logic_version = logic_version or settings.logic_version
        self._cache: dict[str, str] = {}

    def _get_prompt_path(self, agent_name: str) -> Path:
        """
        Get path to prompt file for an agent.

        Args:
            agent_name: Name of the agent (e.g., 'clarifier', 'criteria_builder')

        Returns:
            Path to the prompt file
        """
        # Get project root (assuming prompts/ is at project root)
        project_root = Path(__file__).parent.parent.parent
        prompt_dir = project_root / "prompts" / self.logic_version
        return prompt_dir / f"{agent_name}.txt"

    def load_prompt(self, agent_name: str) -> str:
        """
        Load prompt template for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Prompt template content

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        # Check cache first
        cache_key = f"{self.logic_version}:{agent_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Load from file
        prompt_path = self._get_prompt_path(agent_name)
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_path}. "
                f"Expected at prompts/{self.logic_version}/{agent_name}.txt"
            )

        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Cache it
        self._cache[cache_key] = content
        return content

    def clear_cache(self) -> None:
        """Clear the prompt cache."""
        self._cache.clear()


# Global prompt loader instance
_prompt_loader: Optional[PromptLoader] = None


def get_prompt_loader(logic_version: Optional[str] = None) -> PromptLoader:
    """
    Get or create global prompt loader instance.

    Args:
        logic_version: Optional logic version override

    Returns:
        PromptLoader instance
    """
    global _prompt_loader
    if _prompt_loader is None or (
        logic_version is not None
        and _prompt_loader.logic_version != logic_version
    ):
        _prompt_loader = PromptLoader(logic_version=logic_version)
    return _prompt_loader


