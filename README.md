# DecisionFlow

**Multi-Agent Decision & Trade-off Analyzer**

DecisionFlow is a service that replaces gut-feel decisions with structured, defensible reasoning. Teams submit decision scenarios, and the system orchestrates specialized agents to analyze them from multiple angles, returning machine-readable, explainable recommendations.

## Overview

DecisionFlow is an engineered decision engine, not an LLM wrapper. It provides:

- **Deterministic Reasoning Pipeline**: Fixed execution order with explicit contracts per agent
- **Explicit Bias Detection**: First-class feature detecting and reporting cognitive biases
- **Explainable Scoring Methodology**: Weighted criteria, normalized scores, explicit justification
- **Machine-Readable Outputs**: JSON-structured responses for service consumption
- **Evaluation Harness**: Support for golden decisions and regression testing

## Architecture

DecisionFlow uses a deterministic multi-agent pipeline with specialized agents:

1. **Clarifier Agent**: Identifies missing inputs and asks essential questions
2. **Criteria Builder Agent**: Converts vague goals into weighted evaluation criteria
3. **Bias Checker Agent**: Flags emotional language, sunk-cost bias, optimism bias
4. **Option Evaluator Agent**: Scores each option against criteria with justification
5. **Decision Synthesizer Agent**: Produces final recommendation with confidence level

## Technology Stack

- **Python 3.11**
- **FastAPI** (RESTful API)
- **Pydantic v2** (Data validation)
- **OpenAI SDK** (LLM integration)
- **Redis** (Rate limiting)
- **pytest** (Testing)

## Project Structure

```
decisionflow/
├── app/                    # Application code
│   ├── api/               # FastAPI routes and endpoints
│   ├── agents/            # Agent implementations
│   ├── orchestration/     # Pipeline execution
│   ├── schemas/           # Pydantic models
│   ├── validation/        # Schema validation
│   ├── evaluation/        # Evaluation harness
│   ├── llm/               # LLM client wrapper
│   ├── core/              # Core utilities
│   └── metrics/           # Metrics collection
├── tests/                  # Test suite
├── prompts/               # Prompt templates (versioned)
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

## Getting Started

### Prerequisites

- Python 3.10+
- OpenAI API key
- Redis (optional, for rate limiting - not required yet)

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   ```
   **Note:** Default model is `gpt-3.5-turbo` (widely available). If you have access to GPT-4, you can use `gpt-4` or `gpt-4-turbo-preview`.
4. Run the application: `uvicorn app.main:app --reload`

### Development

- Run tests: `pytest`
- Format code: `ruff format .`
- Type check: `mypy app/`

## API Documentation

Once running, visit:
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
