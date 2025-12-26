# How to Use DecisionFlow

## What is DecisionFlow?

DecisionFlow is a **Multi-Agent Decision & Trade-off Analyzer** - a service that helps you make better decisions by:

1. **Analyzing decision scenarios** through specialized AI agents
2. **Detecting cognitive biases** (sunk cost, confirmation bias, etc.)
3. **Providing structured recommendations** with weighted criteria and confidence scores
4. **Returning machine-readable JSON** that you can integrate into workflows

### Example Use Cases

- **"Should we build feature X now or postpone it?"**
- **"Which vendor should we choose?"**
- **"Should we hire now or wait 3 months?"**
- **"Is this architecture overkill for our scale?"**
- **"Which market should we enter first?"**

## Current Status

**⚠️ Note:** The app is currently in **early development**. Only operational endpoints are implemented:
- ✅ `/health` - Service liveness check
- ✅ `/ready` - Dependency readiness check
- 🚧 `/v1/decisions/analyze` - Main decision endpoint (coming soon)

## The `/ready` Endpoint Explained

### What It Does

The `/ready` endpoint is a **readiness probe** that checks if the service has all its dependencies available and is ready to handle requests.

### What It Receives

**HTTP Method:** `GET`  
**URL:** `http://localhost:8000/ready`  
**Headers:** None required (no authentication needed)  
**Body:** None

### What It Returns

#### Success Response (200 OK)

When **all dependencies are available**:

```json
{
  "status": "ready",
  "checks": {
    "redis": true,
    "openai": true
  }
}
```

**Meaning:**
- ✅ Service is ready to handle requests
- ✅ Redis is connected (needed for rate limiting)
- ✅ OpenAI API key is configured (needed for AI agents)

#### Failure Response (503 Service Unavailable)

When **any dependency is unavailable**:

```json
{
  "detail": {
    "status": "not_ready",
    "checks": {
      "redis": false,
      "openai": false
    }
  }
}
```

**Meaning:**
- ❌ Service is NOT ready to handle requests
- ❌ One or more dependencies are missing/unavailable
- ⚠️ The service will still run, but may not function correctly

### What It Checks

1. **Redis Connectivity**
   - Tries to connect to Redis (for rate limiting)
   - Sends a PING command
   - Timeout: 2 seconds
   - **Why needed:** Rate limiting per API key

2. **OpenAI Configuration**
   - Checks if `OPENAI_API_KEY` is set in environment
   - Verifies it's not empty
   - **Why needed:** All AI agents use OpenAI for decision analysis

### When to Use `/ready`

- **Orchestration systems** (Kubernetes, Docker Swarm) use it to know when to route traffic
- **Load balancers** check it before sending requests
- **Monitoring tools** use it for health dashboards
- **You** can check it manually to verify setup before making requests

### Example Usage

**PowerShell:**
```powershell
# Check if service is ready
$response = Invoke-WebRequest -Uri "http://localhost:8000/ready"
$response.Content | ConvertFrom-Json
```

**cURL:**
```bash
curl http://localhost:8000/ready
```

**Browser:**
```
http://localhost:8000/ready
```

**Python:**
```python
import requests
response = requests.get("http://localhost:8000/ready")
print(response.status_code)
print(response.json())
```

## Other Endpoints

### `/health` - Liveness Check

**What it does:** Simple check if the service is running  
**Returns:** `{"status": "ok"}`  
**When to use:** Quick check if service is alive (doesn't check dependencies)

### `/` - Root Endpoint

**What it does:** Returns basic service information  
**Returns:**
```json
{
  "service": "DecisionFlow",
  "version": "v1.0.0",
  "status": "running"
}
```

### `/docs` - Interactive API Documentation

**What it does:** Swagger UI for exploring all endpoints  
**URL:** `http://localhost:8000/docs`  
**When to use:** Explore available endpoints and test them interactively

## Future: The Main Endpoint

Once implemented, you'll use:

**POST `/v1/decisions/analyze`**

**Request:**
```json
{
  "decision_context": "Should we build feature X now or postpone it?",
  "options": ["Build now", "Postpone 3 months", "Postpone 6 months"],
  "constraints": {
    "budget": 50000,
    "timeline": "Q2 2024"
  }
}
```

**Response:**
```json
{
  "decision": "Build feature X now",
  "recommended_option": "Build now",
  "confidence": 0.78,
  "criteria": [
    {"name": "time_to_market", "weight": 0.4},
    {"name": "resource_availability", "weight": 0.3},
    {"name": "strategic_value", "weight": 0.3}
  ],
  "scores": {
    "Build now": {
      "total_score": 0.82,
      "breakdown": {...}
    },
    "Postpone 3 months": {...},
    "Postpone 6 months": {...}
  },
  "biases_detected": [
    {
      "type": "optimism_bias",
      "description": "Unjustified high confidence in 'Build now' option"
    }
  ],
  "trade_offs": [...],
  "assumptions": [...],
  "request_id": "req_123456"
}
```

## Summary

- **`/ready`** = "Can this service handle requests right now?"
- **Checks:** Redis + OpenAI configuration
- **Returns:** Status of each dependency
- **Use it:** Before making important requests, or for monitoring

The app is being built to help you make better decisions through structured AI analysis!

