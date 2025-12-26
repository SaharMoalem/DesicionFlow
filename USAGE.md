# DecisionFlow - Usage Guide

## Implementation Status

### ✅ Completed (Core Functionality)

**Epic 2: Core Decision Analysis Pipeline** - **COMPLETE**
- ✅ Story 2.9: Pipeline Orchestration
- ✅ Story 2.10: Schema Validation Service
- ✅ Story 2.11: Decision Analysis API Endpoint
- ✅ Story 2.12: Error Handling and Standardized Error Responses

**What's Working:**
- ✅ All 5 agents implemented (Clarifier, Criteria Builder, Bias Checker, Option Evaluator, Decision Synthesizer)
- ✅ Deterministic pipeline execution
- ✅ Schema validation at request, agent steps, and response
- ✅ Schema repair mechanism
- ✅ POST `/v1/decisions/analyze` endpoint
- ✅ Standardized error handling with request_id
- ✅ Health and readiness endpoints
- ✅ 163 unit tests passing

### ⏳ Pending (Optional for MVP)

**Epic 3: Security & Access Control**
- ⏳ Story 3.1: API Key Authentication
- ⏳ Story 3.2: Rate Limiting
- ⏳ Story 3.3: Input Sanitization

**Note:** The app is fully functional without these features. They can be added later for production use.

## Quick Start

### 1. Prerequisites

- Python 3.10+ (you have 3.10.10 ✅)
- OpenAI API key
- Redis (optional, for rate limiting - not required yet)

### 2. Setup

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create .env file with your OpenAI API key:
# Required:
OPENAI_API_KEY=your-api-key-here

# Optional (default: gpt-3.5-turbo):
OPENAI_MODEL=gpt-3.5-turbo
```

**Important:** If you get a "model_not_found" error, make sure you're using a model you have access to:
- `gpt-3.5-turbo` - Available to all users (recommended)
- `gpt-4` - Requires GPT-4 access
- `gpt-4-turbo-preview` - Requires GPT-4 access

### 3. Run the Application

```bash
# Start the FastAPI server
uvicorn app.main:app --reload

# The app will be available at:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Health: http://localhost:8000/health
```

### 4. Test the API

#### Using curl:

```bash
# Health check
curl http://localhost:8000/health

# Analyze a decision
curl -X POST http://localhost:8000/v1/decisions/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "decision_context": "Should we choose AWS or GCP for our new microservice? We need high scalability and low cost.",
    "options": ["AWS", "GCP"],
    "constraints": {"budget": 50000}
  }'
```

#### Using Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/decisions/analyze",
    json={
        "decision_context": "Should we build feature X now or postpone it?",
        "options": ["Build now", "Postpone"],
        "constraints": {"budget": 100000, "timeline": "3 months"}
    }
)

print(response.json())
```

#### Using the Interactive API Docs:

1. Start the server: `uvicorn app.main:app --reload`
2. Open browser: http://localhost:8000/docs
3. Click on `POST /v1/decisions/analyze`
4. Click "Try it out"
5. Enter your decision request
6. Click "Execute"

## API Endpoint Details

### POST `/v1/decisions/analyze`

**Request Body:**
```json
{
  "decision_context": "Problem description and decision context (10-10000 chars)",
  "options": ["Option 1", "Option 2", ...],  // 2-20 options
  "constraints": {  // Optional
    "budget": 50000,
    "timeline": "3 months"
  },
  "criteria_preferences": ["cost", "speed"],  // Optional
  "context_metadata": {}  // Optional
}
```

**Response:**
```json
{
  "decision": "...",
  "options": ["Option 1", "Option 2"],
  "criteria": [
    {
      "name": "Cost",
      "weight": 0.4,
      "rationale": "..."
    }
  ],
  "scores": {
    "Option 1": {
      "total_score": 0.75,
      "breakdown": [...]
    }
  },
  "winner": "Option 1",
  "confidence": 0.85,
  "confidence_breakdown": {
    "input_completeness": 0.9,
    "agent_agreement": 0.85,
    "evidence_strength": 0.8,
    "bias_impact": 0.9
  },
  "biases_detected": [],
  "trade_offs": [...],
  "assumptions": [...],
  "risks": [],
  "what_would_change_decision": [...],
  "meta": {
    "api_version": "v1",
    "logic_version": "1.0.0",
    "schema_version": "1.0.0"
  },
  "request_id": "uuid-here"
}
```

## Example Use Cases

### 1. Technology Choice
```json
{
  "decision_context": "We need to choose a database for our new application. Requirements: high read performance, horizontal scaling, and cost-effective.",
  "options": ["PostgreSQL", "MongoDB", "DynamoDB"]
}
```

### 2. Hiring Decision
```json
{
  "decision_context": "Should we hire a senior engineer now or wait 3 months? We have budget but need to balance immediate needs vs. long-term planning.",
  "options": ["Hire now", "Wait 3 months"],
  "constraints": {"budget": 150000, "timeline": "Q1"}
}
```

### 3. Feature Prioritization
```json
{
  "decision_context": "Which feature should we build first: user authentication, payment integration, or analytics dashboard?",
  "options": ["Authentication", "Payments", "Analytics"],
  "criteria_preferences": ["user value", "technical complexity", "revenue impact"]
}
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/app/api/v1/test_decisions.py -v
```

## Troubleshooting

### Issue: "OpenAI API key is not configured"
**Solution:** Make sure your `.env` file contains `OPENAI_API_KEY=your-key-here`

### Issue: "Redis connection failed" (for /ready endpoint)
**Solution:** Redis is optional. The app works without it. If you want Redis:
- Install Redis: `docker run -d -p 6379:6379 redis:7-alpine`
- Or update `.env` with `REDIS_HOST=localhost`

### Issue: Import errors
**Solution:** Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Next Steps (Optional)

To add production-ready features:

1. **API Key Authentication** (Story 3.1)
   - Add API key validation middleware
   - Protect endpoints with authentication

2. **Rate Limiting** (Story 3.2)
   - Implement token-bucket rate limiting
   - Add rate limit headers to responses

3. **Input Sanitization** (Story 3.3)
   - Add input sanitization to prevent prompt injection
   - Validate and clean user inputs

## Support

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Readiness Check: http://localhost:8000/ready

