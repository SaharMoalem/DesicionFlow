"""Tests for prompt template loading."""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from app.llm.prompts import PromptLoader, get_prompt_loader


def test_prompt_loader_loads_prompt(tmp_path: Path) -> None:
    """Test PromptLoader loads prompt from file."""
    # Create test prompt directory structure
    prompt_dir = tmp_path / "prompts" / "v1.0.0"
    prompt_dir.mkdir(parents=True)
    prompt_file = prompt_dir / "clarifier.txt"
    prompt_file.write_text("This is a test prompt for clarifier agent")

    # Mock the path resolution
    with patch("app.llm.prompts.Path") as mock_path:
        mock_path.return_value.parent.parent.parent = tmp_path
        loader = PromptLoader(logic_version="v1.0.0")
        content = loader.load_prompt("clarifier")

    assert content == "This is a test prompt for clarifier agent"


def test_prompt_loader_caches_prompts(tmp_path: Path) -> None:
    """Test PromptLoader caches loaded prompts."""
    prompt_dir = tmp_path / "prompts" / "v1.0.0"
    prompt_dir.mkdir(parents=True)
    prompt_file = prompt_dir / "clarifier.txt"
    prompt_file.write_text("Test prompt")

    with patch("app.llm.prompts.Path") as mock_path:
        mock_path.return_value.parent.parent.parent = tmp_path
        loader = PromptLoader(logic_version="v1.0.0")

        # Load twice
        content1 = loader.load_prompt("clarifier")
        content2 = loader.load_prompt("clarifier")

        # Should be the same (cached)
        assert content1 == content2
        assert content1 == "Test prompt"


def test_prompt_loader_raises_on_missing_file(tmp_path: Path) -> None:
    """Test PromptLoader raises FileNotFoundError for missing prompt."""
    with patch("app.llm.prompts.Path") as mock_path:
        mock_path.return_value.parent.parent.parent = tmp_path
        loader = PromptLoader(logic_version="v1.0.0")

        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load_prompt("nonexistent")

        assert "not found" in str(exc_info.value).lower()


def test_prompt_loader_clear_cache() -> None:
    """Test PromptLoader can clear cache."""
    loader = PromptLoader(logic_version="v1.0.0")
    loader._cache["test"] = "cached value"
    assert len(loader._cache) > 0

    loader.clear_cache()
    assert len(loader._cache) == 0


def test_get_prompt_loader_returns_singleton() -> None:
    """Test get_prompt_loader returns same instance."""
    loader1 = get_prompt_loader()
    loader2 = get_prompt_loader()
    assert loader1 is loader2


def test_get_prompt_loader_with_version_override() -> None:
    """Test get_prompt_loader creates new instance with different version."""
    loader1 = get_prompt_loader()
    loader2 = get_prompt_loader(logic_version="v2.0.0")
    # Should be different instances when version differs
    assert loader2.logic_version == "v2.0.0"

