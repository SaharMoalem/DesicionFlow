# Prompt Templates

This directory contains versioned prompt templates for all agents.

## Versioning

Prompts are organized by logic version (e.g., `v1.0.0/`). Each version directory contains:
- `clarifier.txt`: Prompt for Clarifier Agent
- `criteria_builder.txt`: Prompt for Criteria Builder Agent
- `bias_checker.txt`: Prompt for Bias Checker Agent
- `option_evaluator.txt`: Prompt for Option Evaluator Agent
- `decision_synthesizer.txt`: Prompt for Decision Synthesizer Agent
- `repair.txt`: Prompt for schema repair

## Usage

Prompts are loaded by `app/llm/prompts.py` based on the `LOGIC_VERSION` environment variable.

## Version Management

- Prompts are git-versioned (not stored in database)
- Logic version is pinned per environment
- Changes to prompts require creating a new version directory
- Old versions are preserved for regression testing


