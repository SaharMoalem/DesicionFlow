# DecisionFlow Setup Guide

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# Required: Your OpenAI API key
OPENAI_API_KEY=sk-your-api-key-here

# Optional: Model selection (default: gpt-3.5-turbo)
OPENAI_MODEL=gpt-3.5-turbo

# Optional: Other settings
OPENAI_TEMPERATURE=0.0
OPENAI_MAX_TOKENS=2000
```

### 3. Available Models

**Recommended (Widely Available):**
- `gpt-3.5-turbo` - Fast, cost-effective, good quality (default)
- `gpt-3.5-turbo-16k` - Same as above but with 16k context window

**If You Have Access:**
- `gpt-4` - Higher quality, more expensive
- `gpt-4-turbo-preview` - Latest GPT-4 variant
- `gpt-4-0125-preview` - Specific GPT-4 version

**To Check Available Models:**
1. Visit: https://platform.openai.com/api-keys
2. Check your account tier and available models
3. Or test with: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

### 4. Start the Application

```bash
# Start backend
uvicorn app.main:app --reload

# Open browser
# Frontend: http://localhost:8000/
# API Docs: http://localhost:8000/docs
```

## Troubleshooting

### Error: "model_not_found" or "does not exist or you do not have access"

**Solution:** Change the model in your `.env` file:
```
OPENAI_MODEL=gpt-3.5-turbo
```

This model is available to all OpenAI API users.

### Error: "OpenAI API key is not configured"

**Solution:** Make sure your `.env` file exists and contains:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Error: "Redis connection failed"

**Solution:** Redis is optional. The app works without it. If you want Redis:
```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or install locally and update .env
REDIS_HOST=localhost
```

## Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/app/api/v1/test_decisions.py -v

# Test with coverage
pytest --cov=app --cov-report=html
```

## Frontend Usage

1. Start the backend: `uvicorn app.main:app --reload`
2. Open: http://localhost:8000/
3. Enter your decision in natural language
4. Click "Analyze Decision"

Example input:
```
Should we choose AWS or GCP for our new microservice? 
We need high scalability and low cost, with a budget of $50,000.
```

