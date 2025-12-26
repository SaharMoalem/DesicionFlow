---
project_name: 'DesicionFlow'
user_name: 'User'
date: '2025-12-23'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality', 'workflow_rules', 'critical_rules']
status: 'complete'
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

**Core Technologies:**
- **Python:** 3.11 (use `python:3.11-slim` for Docker)
- **FastAPI:** Latest stable (auto-generates OpenAPI 3.0 spec)
- **Pydantic:** v2 (required for `extra="forbid"` and validation features)
- **OpenAI SDK:** Latest (wrapped in `app/llm/client.py` for abstraction)
- **Redis:** Required for rate limiting (token bucket per API key)
- **pytest:** Latest + `pytest-asyncio` for async tests
- **Docker:** Multi-stage builds with `python:3.11-slim` base

**Key Dependencies:**
- `slowapi` or custom Redis-backed middleware for rate limiting
- `ruff` or `black` for code formatting
- `mypy` for type checking (optional but recommended)

**Version Constraints:**
- Must use Pydantic v2 (not v1) - v2 has different validation behavior
- Python 3.11+ required for async/await features and type hints
- FastAPI requires Python 3.8+ but we use 3.11 for performance

## Critical Implementation Rules

### Language-Specific Rules (Python)

**Type Hints & Annotations:**
- Use type hints for all function parameters and return types
- Use `typing` module for complex types (Optional, List, Dict, etc.)
- Async functions must be typed: `async def execute(self, state: PipelineState) -> ClarifierOutput:`
- Use `from __future__ import annotations` if needed for forward references

**Async/Await Patterns:**
- All agent methods must be `async def`
- Use `asyncio.gather()` for parallel calls within agents (e.g., scoring multiple options)
- Never mix sync and async code - use `asyncio.run()` only at application entry point
- Use async context managers for resource management (LLM client, Redis connections)

**Import Conventions:**
- Absolute imports: `from app.agents.clarifier import Clarifier`
- Group imports: stdlib, third-party, local (separated by blank lines)
- Use `from typing import` for type hints, not runtime types

**Error Handling:**
- Raise typed exceptions: `ValidationError`, `LLMError`, `AgentError`
- Use `try/except` with specific exception types, not bare `except:`
- Always include context in error messages: `f"Agent {agent_name} failed: {error}"`

**Pydantic Model Requirements:**
- All data structures MUST be Pydantic models (not dataclasses or plain dicts)
- Always set `model_config = {"extra": "forbid"}` to prevent schema drift
- Use `Field()` for validation, defaults, and aliases
- Use enums for constrained string values: `BiasType`, `DecisionStatus`, `ErrorCode`

### Framework-Specific Rules (FastAPI)

**API Endpoint Patterns:**
- All endpoints under `/v1/` prefix except operational endpoints (`/health`, `/ready`)
- Use FastAPI path parameters: `{decision_id}` not `:id` or query strings for resource IDs
- Use `@router.post("/v1/decisions/analyze")` decorator pattern
- Request/response models must be Pydantic models (FastAPI auto-validates)

**Dependency Injection:**
- Use FastAPI dependencies for auth, request_id extraction: `Depends(get_api_key)`
- Dependencies in `app/api/dependencies.py`, not inline
- Request-scoped dependencies only (no global state)

**Async Route Handlers:**
- All route handlers must be `async def`
- Use `await` for all async operations (LLM calls, Redis, validation)
- Return Pydantic models directly (FastAPI auto-serializes to JSON)

**Error Responses:**
- Use `HTTPException` for standard HTTP errors (401, 404, 429)
- Custom error format: `{"error": {"code": "...", "message": "...", "details": {...}}, "request_id": "..."}`
- Transform all exceptions to standardized `ErrorResponse` format at API layer

**Middleware Order:**
- Request ID generation → Authentication → Rate Limiting → Route handler
- Middleware in `app/api/middleware/` directory

### Testing Rules

**Test Organization:**
- Test files: `test_<module_name>.py` (e.g., `test_clarifier.py`)
- Test structure mirrors source: `tests/app/agents/test_clarifier.py` mirrors `app/agents/clarifier.py`
- Golden decisions: `tests/golden/decision_<type>_<id>/` with `input.json`, `expected_output.json`, `metadata.yaml`

**Async Test Patterns:**
- Use `pytest.mark.asyncio` for async test functions
- Use `AsyncMock` from `unittest.mock` for mocking async functions
- Use `pytest-asyncio` fixtures for async setup/teardown

**Mock Usage:**
- Mock LLM client responses (never call real OpenAI API in tests)
- Mock Redis for rate limiting tests
- Use fixtures in `tests/conftest.py` for shared mocks

**Golden Decision Tests:**
- Each golden case is a folder with input, expected output, metadata
- Use structured comparison (not semantic similarity)
- Hard gates: schema validity, determinism (same input → same output), invariant assertions

**Test Coverage:**
- Unit tests for each agent, validation service, LLM client
- Integration tests for pipeline execution, API endpoints
- Golden decision tests for regression testing across logic versions

### Code Quality & Style Rules

**Naming Conventions (CRITICAL - Enforced):**
- **Modules:** `snake_case.py` - `clarifier.py`, `criteria_builder.py`
- **Classes:** `PascalCase` - `Clarifier`, `CriteriaBuilder`, `PipelineState`
- **Functions:** `snake_case()` - `process_decision()`, `validate_schema()`
- **Variables:** `snake_case` - `pipeline_state`, `request_id`
- **Constants:** `UPPER_SNAKE_CASE` - `MAX_RETRIES`, `DEFAULT_TIMEOUT`
- **Agent classes:** `PascalCase` WITHOUT "Agent" suffix - `Clarifier` not `ClarifierAgent`
- **JSON fields:** `snake_case` throughout - `{"request_id": "...", "confidence_score": 0.78}`

**Code Formatting:**
- Use `ruff` or `black` for formatting (configured in project)
- Use `mypy` for type checking (strict mode recommended)
- Line length: 100 characters (or project default)

**File Organization:**
- One class per file: `app/agents/clarifier.py` contains only `Clarifier` class
- Related Pydantic models together: `app/schemas/decision.py` has `DecisionRequest`, `DecisionResponse`
- Single config file: `app/core/config.py` exports `Settings` object (Pydantic BaseSettings)

**Documentation:**
- Docstrings for all public classes and functions (Google or NumPy style)
- Type hints serve as inline documentation
- Comments for non-obvious business logic, not obvious code

### Development Workflow Rules

**Project Structure (MUST Follow):**
```
app/
├── api/              # FastAPI routes and middleware
├── agents/           # Agent implementations (one file per agent)
├── orchestration/    # Pipeline orchestration
├── schemas/          # Pydantic models
├── validation/       # Schema validation service
├── evaluation/       # Evaluation harness
├── core/             # Core utilities (config, logging, exceptions)
├── llm/              # LLM client wrapper
└── metrics/          # Metrics collection
```

**Request ID Propagation (CRITICAL):**
- Generate UUID v4 at request entry point (API layer)
- Pass `request_id` through `PipelineState` to all components
- Include in ALL logs, metrics, and responses
- Format: `req_<uuid>` or just UUID

**Logging Requirements:**
- Structured logging: JSON format for production, key-value pairs for development
- Include `request_id` in ALL log entries
- Log levels: DEBUG (agent step outputs), INFO (request received), WARNING (retry), ERROR (failure), CRITICAL (system failure)
- **NEVER log raw user input or LLM prompts/responses** (security/privacy)
- Log structured metadata only: `{"request_id": "...", "agent": "clarifier", "duration_ms": 150}`

**Error Handling Flow:**
1. Agent raises typed exception (`AgentError`, `ValidationError`, `LLMError`)
2. Orchestration catches and logs with full context
3. Transform to `ErrorResponse` format at API layer
4. Return standardized error with `request_id`

**Retry Logic:**
- Centralized in LLM client wrapper (`app/llm/retry.py`), NOT in individual agents
- Max 2 retries with exponential backoff + jitter
- Retry only for: timeouts, transient 5xx errors, network errors
- NO retry for: 4xx errors, schema validation failures, business logic errors

**Validation Timing (CRITICAL):**
- Validate request payload immediately on receipt (API layer)
- Validate agent output immediately after agent execution (orchestration layer)
- Validate final response before returning (API layer)
- Use centralized validation service (`app/validation/service.py`)
- Fail fast with clear error messages - do not continue with invalid data

### Critical Don't-Miss Rules

**Anti-Patterns to AVOID:**
- ❌ **Never log raw user input or LLM prompts/responses** - security/privacy risk
- ❌ **Never use `{data: ..., error: ...}` wrapper pattern** - use direct response or error envelope
- ❌ **Never mix sync and async code** - all agent methods must be async
- ❌ **Never skip schema validation** - validate at request, each agent step, and response
- ❌ **Never use dataclasses or plain dicts** - all data structures must be Pydantic models
- ❌ **Never add "Agent" suffix to agent class names** - use `Clarifier` not `ClarifierAgent`
- ❌ **Never use camelCase for JSON fields** - use `snake_case` throughout
- ❌ **Never continue processing with invalid data** - fail fast on validation errors
- ❌ **Never implement retry logic in agents** - use centralized retry in LLM client
- ❌ **Never omit `request_id` from logs or responses** - required for correlation

**Deterministic Pipeline Requirements:**
- Agents execute in FIXED order: Clarifier → Criteria Builder → Bias Checker → Option Evaluator → Decision Synthesizer
- Each agent receives only the subset of `PipelineState` it needs
- Agents write structured outputs to `PipelineState`, not text
- Use low temperature (or fixed) for LLM calls to ensure determinism
- Record `model_id`, `temperature`, `logic_version` in metadata

**Schema Validation Requirements:**
- All Pydantic models MUST have `model_config = {"extra": "forbid"}`
- Schema repair: one-shot attempt using dedicated repair function, then fail if still invalid
- Schema version tracked in `PipelineState` and included in all responses
- Backward compatible within `/v1` API version

**Security Rules:**
- Sanitize inputs at API layer before pipeline execution (`app/core/sanitization.py`)
- Pass only validated, sanitized data to agents (structured subsets)
- No tool execution - agents do not execute external tools or code
- API keys from environment allowlist (MVP), never hardcode
- HTTPS only (no unencrypted HTTP)

**Performance Requirements:**
- P50 ≤ 3s, P95 ≤ 5s, hard timeout 10s
- Bounded concurrency for LLM calls (strict timeouts, limited retries)
- Stateless design - no shared state between requests
- All state in request-scoped `PipelineState` object

**Version Metadata (REQUIRED in all responses):**
- Include `api_version`, `logic_version`, `schema_version` in response `meta` field
- Logic version from `prompts/<logic_version>/` directory
- Schema version from Pydantic model definitions
- API version from URL path (`/v1/...`)

**Configuration Access:**
- Single `Settings` object from `app/core/config.py` (Pydantic BaseSettings)
- Import: `from app.core.config import settings`
- Access: `settings.api_keys`, `settings.logic_version`
- Load from environment variables, never hardcode secrets

---

## Usage Guidelines

**For AI Agents:**

- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Update this file if new patterns emerge during implementation
- Reference the architecture document (`_bmad-output/architecture.md`) for detailed architectural decisions

**For Humans:**

- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review quarterly for outdated rules
- Remove rules that become obvious over time
- Maintain consistency with architecture document

**Last Updated:** 2025-12-23

