# DecisionFlow

**Multi-Agent Decision & Trade-off Analyzer**

DecisionFlow is a full-stack application that replaces gut-feel decisions with structured, defensible reasoning. Teams submit decision scenarios through an intuitive web interface, and the system orchestrates specialized agents to analyze them from multiple angles, returning machine-readable, explainable recommendations.

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

### Backend
- **Python 3.11**
- **FastAPI** (RESTful API)
- **Pydantic v2** (Data validation)
- **OpenAI SDK** (LLM integration)
- **Redis** (Rate limiting)
- **pytest** (Testing)

### Frontend
- **HTML5** (Structure)
- **CSS3** (Styling)
- **Vanilla JavaScript** (Client-side logic)
- **Natural Language Processing** (Free-text input parsing)

## Project Structure

```
decisionflow/
├── app/                    # Backend application code
│   ├── api/               # FastAPI routes and endpoints
│   ├── agents/            # Agent implementations
│   ├── orchestration/     # Pipeline execution
│   ├── schemas/           # Pydantic models
│   ├── validation/        # Schema validation
│   ├── evaluation/        # Evaluation harness
│   ├── llm/               # LLM client wrapper
│   ├── core/              # Core utilities
│   └── metrics/           # Metrics collection
├── frontend/              # Frontend application
│   ├── index.html         # Main HTML structure
│   ├── styles.css         # Styling
│   └── app.js             # Client-side logic and API integration
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
5. Open your browser and navigate to: `http://localhost:8000`

### Development

- Run tests: `pytest`
- Format code: `ruff format .`
- Type check: `mypy app/`

## Usage

### Web Interface

The application includes a user-friendly web interface accessible at `http://localhost:8000`. Simply enter your decision question in natural language, and the system will:

1. Parse your input to extract options and context
2. Run the multi-agent analysis pipeline
3. Display the results with:
   - Recommended option with confidence level
   - Evaluation criteria and weights
   - Option scores
   - Detected biases
   - Trade-offs and risks
   - Assumptions and what would change the decision

**Example Input:**
```
Should we choose AWS or GCP for our new microservice? 
We need high scalability and low cost, with a budget of $50,000.
```

### API Documentation

For programmatic access, the API is fully documented:
- **Interactive API docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative docs**: `http://localhost:8000/redoc` (ReDoc)
- **Health check**: `http://localhost:8000/health`

### API Endpoint

**POST** `/v1/decisions/analyze`

Request body:
```json
{
  "decision_context": "Problem description and decision context",
  "options": ["Option A", "Option B"],
  "constraints": {
    "budget": 50000,
    "timeline": "3 months"
  },
  "criteria_preferences": ["scalability", "cost"]
}
```

Response includes:
- Winner recommendation
- Confidence breakdown
- Detailed scoring per option
- Bias findings
- Trade-offs and risks
- Assumptions
