---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments: ['_bmad-output/prd.md']
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2025-12-23'
project_name: 'DesicionFlow'
user_name: 'User'
date: '2025-12-23'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

The PRD defines 73 functional requirements organized into 11 capability areas:

1. **Decision Analysis Capabilities (FR1-FR10):** Core deterministic multi-agent pipeline with 5 agents in fixed execution order (Clarifier → Criteria Builder → Bias Checker → Option Evaluator → Decision Synthesizer). Each agent has explicit contracts and produces schema-validated outputs.

2. **Schema Validation & Data Integrity (FR11-FR15):** Schema validation required at three critical points: request payload, every agent step output, and final response payload. Schema repair pass before failing with error.

3. **Bias Detection Capabilities (FR16-FR21):** Four core bias types (sunk cost, confirmation, optimism, authority) detected and returned separately from recommendations.

4. **Confidence Scoring Capabilities (FR22-FR27):** Multi-factor confidence calculation based on input completeness, agent agreement, evidence strength, and detected biases.

5. **Explainability Capabilities (FR28-FR32):** Explicit justifications, weighted criteria, trade-off analysis, and documented assumptions in structured output.

6. **Authentication & Authorization (FR33-FR37):** API key authentication (Bearer token or X-API-Key header), single-tenant MVP, rate limiting per API key (60 req/min, burst 20).

7. **Error Handling & Diagnostics (FR38-FR44):** Standardized error envelopes with request_id, typed error codes, retry-after information.

8. **Operational Capabilities (FR45-FR50):** Health/readiness endpoints, version metadata endpoint, version reporting in responses.

9. **Versioning Capabilities (FR51-FR54):** Separate API versioning (/v1/...), logic versioning (prompt bundle), and schema versioning with compatibility checks.

10. **Evaluation & Testing Capabilities (FR55-FR59):** Golden decision test suite, regression testing across versions, testability and auditability demonstration.

11. **Deterministic Execution, Rate Limiting, Documentation (FR60-FR73):** Fixed agent order, explicit contracts, repeatable outputs, audit trails, rate limiting, OpenAPI specification.

**Non-Functional Requirements:**

**Performance (NFR1-NFR10):**
- Response time: P50 ≤ 3s, P95 ≤ 5s, hard timeout 10s
- Concurrency: 50-100 concurrent requests in MVP
- Stateless design for horizontal scaling
- Performance degradation handling with reduced confidence and latency warnings

**Security (NFR11-NFR22):**
- API key authentication, HTTPS only
- Input sanitization to prevent prompt injection
- No raw input logging by default
- GDPR-aware design if persistence enabled
- No domain-specific compliance required in MVP

**Scalability (NFR23-NFR30):**
- Stateless API design
- Externalized configuration
- Rate limiting per API key (60 req/min, burst 20)
- Fail-fast with 429 responses when capacity exceeded

**Integration (NFR31-NFR38):**
- API-first, JSON-only
- Stable schemas as hard requirement
- OpenAPI 3.0 specification
- Deterministic response structure
- Backward compatibility within /v1
- Explicit error codes, no ambiguous responses

**Reliability & Resilience (NFR39-NFR49):**
- 99.5% uptime target
- Health/readiness endpoints
- Dependency failure handling (structured errors, no degraded decisions)
- Observability: request_id correlation, metrics (latency P50/P95, error rate, schema failure rate)
- Platform-level incident treatment

**Scale & Complexity:**

- **Primary domain:** API Backend Service
- **Complexity level:** Medium (high technical rigor requirements, low domain complexity)
- **Estimated architectural components:** 8-10 major components
  - API Gateway/Layer (request handling, routing)
  - Agent Orchestration Engine (deterministic pipeline execution)
  - Schema Validation Service (request, agent step, response validation)
  - Authentication & Authorization Service (API key validation, rate limiting)
  - Agent Pipeline Components (5 specialized agents)
  - Evaluation Harness (regression testing, golden decisions)
  - Observability & Monitoring (metrics, logging, request correlation)
  - Versioning System (API, logic, schema version management)

### Technical Constraints & Dependencies

**Architectural Constraints:**

1. **Deterministic Execution:** Fixed agent execution order must be enforced. Cannot allow emergent or non-deterministic behavior.

2. **Schema-First Design:** JSON Schema validation required at three points: request receipt, every agent step output, final response. Schema repair pass before failing.

3. **Stateless Architecture:** Required for horizontal scaling. No session state, no in-memory state between requests.

4. **Versioning Separation:** API version, logic version (prompt bundle), and schema version must be independently versioned and tracked.

5. **No Persistence in MVP:** Request/response model only. No decision storage, no replay endpoints in MVP.

6. **Performance Bounds:** Agent calls must be bounded with timeout handling. Latency must be predictable (P50 ≤ 3s, P95 ≤ 5s).

7. **Machine-Readable Outputs:** All outputs must be JSON-structured, schema-validated, and designed for service consumption (not human-readable prose).

**External Dependencies:**

1. **LLM/Model Dependencies:** Model and tool dependencies must be reachable. Readiness endpoint must verify dependency availability.

2. **Schema Validation Libraries:** JSON Schema validation libraries required for request, agent step, and response validation.

3. **Rate Limiting Infrastructure:** Token bucket algorithm implementation for rate limiting per API key.

4. **Observability Infrastructure:** Metrics collection, logging infrastructure, request_id correlation system.

5. **Configuration Management:** Externalized configuration for prompt versions, feature flags, environment separation.

**Technical Dependencies (Future):**

- Decision persistence (post-MVP)
- Multi-tenant support infrastructure
- Analytics and aggregation capabilities
- Webhook callback infrastructure

### Cross-Cutting Concerns Identified

**1. Schema Validation:**
- Required at request receipt (FR11)
- Required at every agent step output (FR12)
- Required at response generation (FR13)
- Schema repair pass before failing (FR14)
- Must not add unpredictable latency (NFR4)
- Schema versioning separate from API versioning (FR51-FR54)

**2. Error Handling:**
- Standardized error envelopes with error code, message, details, request_id (FR38)
- Typed error codes for validation, processing, system, auth errors (FR40-FR43)
- Retry-after information for rate limits (FR44)
- No ambiguous or partial responses (NFR37)

**3. Observability:**
- Request_id on every response for correlation (FR39, NFR45)
- Agent-level metrics and monitoring (from user journeys)
- Schema validation error tracking (from user journeys)
- Basic metrics: latency (P50, P95), error rate, schema failure rate (NFR46)
- Structured logging with request_id correlation (NFR47)

**4. Versioning:**
- API versioning via URL path (/v1/...) (FR51)
- Logic versioning (prompt bundle version) independent of API version (FR52)
- Schema versioning independent of API and logic versions (FR50, FR53)
- Version compatibility checking via /v1/meta endpoint (FR54)
- Version information in responses (FR53)

**5. Security:**
- Input sanitization to prevent prompt injection (NFR18)
- No raw input logging by default (NFR19)
- Secure API key management (NFR20)
- HTTPS only (NFR13)
- GDPR-aware design if persistence enabled (NFR21)

**6. Performance:**
- Bounded agent calls with timeout handling (from scope)
- Predictable latency targets (P50 ≤ 3s, P95 ≤ 5s) (NFR1-NFR2)
- Hard timeout 10s (NFR3)
- Performance degradation handling (reduced confidence, latency warnings) (NFR8-NFR9)
- No partial or streaming outputs (NFR10)

**7. Testability:**
- Evaluation harness for regression testing (FR55-FR57)
- Golden decision test suite (FR55)
- Output comparison across versions (FR56)
- Testability and auditability demonstration (FR58-FR59)

**8. Deterministic Execution:**
- Fixed agent execution order (FR60)
- Explicit contracts per agent (FR61)
- Repeatable outputs for same input (FR62)
- Audit trails through agent step outputs (FR63)
- Debugging support through structured agent outputs (FR64)

### Architectural Challenges

**1. Deterministic Orchestration:**
- Challenge: Enforce fixed agent execution order while maintaining flexibility for future extensions
- Impact: Core differentiator - must be architected correctly from day one
- Considerations: Agent contract enforcement, pipeline state management, error recovery

**2. Schema Validation Performance:**
- Challenge: Validate at every agent step without adding unpredictable latency
- Impact: NFR4 requires no unpredictable latency from schema validation
- Considerations: Efficient validation libraries, schema repair pass, validation error handling

**3. Agent Contract Enforcement:**
- Challenge: Ensure each agent produces outputs matching explicit contracts
- Impact: Testability and auditability depend on contract compliance
- Considerations: Schema validation at each step, contract definition format, validation failure recovery

**4. Versioning Complexity:**
- Challenge: Manage three independent versioning systems (API, logic, schema)
- Impact: Integration reliability depends on version compatibility
- Considerations: Version metadata endpoint, compatibility checking, version information in responses

**5. Evaluation Harness Integration:**
- Challenge: Build evaluation harness that supports regression testing across prompt versions
- Impact: Engineering maturity and production readiness demonstration
- Considerations: Golden decision test suite, output comparison, regression test automation

**6. Performance Targets:**
- Challenge: Achieve P50 ≤ 3s, P95 ≤ 5s with multi-agent pipeline and LLM calls
- Impact: User experience and integration reliability
- Considerations: Agent call optimization, parallel execution where possible, timeout handling, graceful degradation

**7. Stateless Design with Agent Pipeline:**
- Challenge: Maintain stateless architecture while executing deterministic multi-agent pipeline
- Impact: Horizontal scaling capability
- Considerations: Request-scoped state management, no shared state between requests, agent output passing

**8. Observability at Agent Level:**
- Challenge: Provide agent-level metrics and debugging without impacting performance
- Impact: Operational support and debugging capabilities
- Considerations: Structured logging, metrics collection, request_id correlation, agent step output visibility

## Starter Template Evaluation

### Primary Technology Domain

**API Backend Service** based on project requirements analysis. DecisionFlow is architected as a RESTful API backend that processes decision requests through a deterministic multi-agent pipeline.

### Starter Options Considered

**FastAPI Framework Evaluation:**

FastAPI was selected as the primary framework for DecisionFlow based on the following alignment with project requirements:

**Alignment with Requirements:**
- **Automatic OpenAPI Documentation:** FastAPI automatically generates OpenAPI 3.0 specification (aligns with NFR33 - OpenAPI specification requirement)
- **Pydantic Data Validation:** Built-in Pydantic models provide schema validation at request/response boundaries (aligns with FR11-FR15 - schema validation requirements)
- **Async Support:** Native async/await support enables concurrent request handling and performance optimization (aligns with NFR6 - 50-100 concurrent requests)
- **Type Hints:** Python type hints enable compile-time validation and better developer experience
- **High Performance:** Built on Starlette and Pydantic, providing minimal latency (aligns with NFR1-NFR2 - P50 ≤ 3s, P95 ≤ 5s targets)

**Alternative Frameworks Considered:**
- **Flask:** Lightweight but lacks automatic OpenAPI generation and requires manual schema validation setup
- **Django:** Full-stack framework with more overhead than needed for API-only service
- **PyMS:** Microservices chassis pattern, but adds complexity for single-service MVP

### Selected Starter: Custom FastAPI Structure

**Rationale for Selection:**

A custom FastAPI project structure was chosen over pre-built templates because:

1. **Deterministic Pipeline Architecture:** DecisionFlow's core differentiator is the deterministic multi-agent pipeline. A custom structure allows us to organize code around agent orchestration patterns rather than generic MVC patterns.

2. **Schema Validation at Every Step:** Unlike typical API structures, DecisionFlow requires schema validation at three points (request, each agent step, response). Custom structure enables explicit validation layers.

3. **Evaluation Harness Integration:** The evaluation harness for regression testing is a core capability that requires specific project organization not found in generic templates.

4. **Agent Contract Enforcement:** Custom structure allows us to clearly separate agent contracts, implementations, and validation logic.

5. **Minimal Boilerplate:** Generic templates include features (database ORMs, authentication systems, etc.) that aren't needed for MVP, adding unnecessary complexity.

**Initialization Approach:**

```bash
# Create project structure manually following FastAPI best practices
# Custom structure optimized for deterministic agent pipeline architecture
```

**Project Structure Foundation:**

```
decisionflow/
├── app/
│   ├── api/              # API routes and endpoints
│   ├── agents/           # Agent implementations (Clarifier, Criteria Builder, etc.)
│   ├── orchestration/    # Pipeline orchestration engine
│   ├── schemas/          # Pydantic models for validation
│   ├── validation/       # Schema validation service
│   ├── evaluation/       # Evaluation harness
│   └── core/             # Core utilities (config, logging, etc.)
├── tests/
├── docs/
└── requirements.txt
```

### Architectural Decisions Provided by Starter

**Language & Runtime:**
- Python 3.8+ with async/await support
- Type hints throughout codebase for validation and IDE support
- Modern Python features (dataclasses, type annotations, async context managers)

**API Framework:**
- FastAPI for REST API endpoints
- Automatic OpenAPI 3.0 specification generation
- Interactive API documentation (Swagger UI, ReDoc)
- Dependency injection system for clean architecture

**Data Validation:**
- Pydantic models for request/response validation
- JSON Schema generation from Pydantic models
- Type-safe data structures throughout application
- Validation error handling with clear error messages

**Async Support:**
- Native async/await for concurrent request handling
- Async HTTP client support for LLM API calls
- Non-blocking I/O for improved performance
- Async context managers for resource management

**Build Tooling:**
- Python package management (pip, poetry, or uv)
- Virtual environment isolation
- Dependency management and versioning
- Development vs. production dependencies

**Testing Framework:**
- pytest for unit and integration testing
- pytest-asyncio for async test support
- Test fixtures and mocking capabilities
- Coverage reporting

**Code Organization:**
- Modular structure organized by domain (agents, orchestration, validation)
- Separation of concerns (API layer, business logic, data validation)
- Clear boundaries between components
- Dependency injection for testability

**Development Experience:**
- Hot reloading with uvicorn development server
- Type checking with mypy (optional)
- Linting with ruff or black
- Debugging support with Python debugger
- Environment-based configuration

**Note:** Project initialization using this custom FastAPI structure should be the first implementation story. The structure will be optimized for DecisionFlow's specific requirements: deterministic agent pipeline, schema validation at every step, evaluation harness, and versioning system.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Agent Orchestration Architecture (deterministic pipeline execution)
- LLM Integration (API client, prompt management, error handling)
- Schema Validation Strategy (validation at every step, repair mechanism)
- Authentication & Security (API keys, rate limiting, input sanitization)
- Infrastructure & Deployment (hosting, containerization, CI/CD)

**Important Decisions (Shape Architecture):**
- Evaluation Harness (regression testing, output comparison)
- Observability & Monitoring (metrics, logging, tracing)
- Configuration Management (prompt versioning, environment separation)

**Deferred Decisions (Post-MVP):**
- Multi-tenant support (database-backed API keys, tenant isolation)
- Decision persistence (storage, replay endpoints)
- Advanced analytics dashboard
- Multi-provider LLM abstraction (beyond OpenAI wrapper)

### Agent Orchestration Architecture

**Execution Pattern:**
- **Default:** Sequential execution in fixed order (Clarifier → Criteria Builder → Bias Checker → Option Evaluator → Decision Synthesizer)
- **Parallelism:** Optional only for sub-tasks inside a step (e.g., scoring multiple options concurrently within Option Evaluator), but pipeline stages remain sequential
- **Rationale:** Deterministic behavior, clear traceability, and easier evaluation. Parallelism is bounded and does not change stage outputs

**Agent Contract Format:**
- **Pydantic models per agent:** `AgentInput` and `AgentOutput` for each stage
- **Shared DecisionContext schema** that evolves stage-by-stage
- **Enforcement:**
  - `model_config = {"extra": "forbid"}` to prevent schema drift
  - Explicit enums for bias types, decision types, etc.
- **Rationale:** Strict contracts are the core differentiator; Pydantic gives validation + typed tooling + OpenAPI alignment

**Pipeline State Management:**
- **Request-scoped state object:** Single in-memory `PipelineState` (Pydantic or dataclass) containing:
  - `request_id`, `api_version`, `logic_version`, `schema_version`
  - Normalized user input
  - Outputs per step (typed)
  - Derived artifacts (criteria, weights, scores, biases)
- **Stateless service:** Do not persist by default in MVP
- **Future persistence:** If persistence is needed later, store final artifacts only, not raw prompts/responses

**Output Passing Mechanism:**
- Agents read from and write to `PipelineState` using structured objects, not text
- Each agent receives only the subset it needs:
  - Clarifier returns `missing_fields` and `questions` (structured)
  - CriteriaBuilder returns `criteria[]` with weights + rationale
  - BiasChecker returns `bias_findings[]` referencing specific fields or phrases
  - OptionEvaluator returns scores per option per criterion + confidence signals
  - Synthesizer returns winner, tradeoffs, assumptions, `what_changes_decision`
- **Rationale:** Reduces prompt injection risk and supports evaluation

**Error Handling / Retries:**
- **Fail-fast by default** for non-recoverable failures; return typed error with `request_id`
- **For recoverable cases:**
  - LLM call retry: max 2 retries with exponential backoff + jitter (timeouts, transient 5xx)
  - Schema repair: 1 repair attempt using strict "return valid JSON for this schema" prompt; if still invalid → fail with `SCHEMA_INVALID`
- **No degraded output in MVP except:**
  - If input is insufficient, return `status="NEEDS_INFO"` with structured questions (from Clarifier)
- **Rationale:** Auditability and trust. Degraded recommendations are worse than explicit uncertainty

**Determinism Requirements:**
- Use a single orchestration runner with:
  - Fixed stage order
  - Deterministic prompt templates per `logic_version`
  - Temperature set low (or fixed) and recorded in meta
- Return meta in every response:
  - `api_version`, `logic_version`, `schema_version`, `model_id`, `request_id`

### LLM Integration

**LLM API Client:**
- **Current:** Wrapper over OpenAI SDK
- **Future:** Provider-agnostic interface for multi-provider support
- **Rationale:** Start simple with OpenAI, design for extensibility

**Async LLM Call Handling:**
- **Bounded concurrency** with strict timeouts and limited retries
- Use `asyncio.gather()` for parallel calls within agents (e.g., scoring multiple options)
- Per-call timeout handling
- Retry logic with exponential backoff (max 2 retries)

**Prompt Management and Versioning:**
- **Git-versioned prompt bundles** per `logic_version`
- **No dynamic prompt edits in MVP**
- Prompt templates stored as files in repository, organized by `logic_version`
- Environment separation: staging vs. production prompt versions

**Model Selection and Configuration:**
- **Pinned model + params per logic_version**
- **Optional fallback model** only on provider failure
- Temperature and other parameters: fixed per `logic_version`, recorded in metadata
- Model selection: shared across pipeline (single model per logic_version)

**Error Handling for LLM Calls:**
- **Fail-fast (except "NEEDS_INFO")**, no degraded outputs
- Retry strategy: max 2 retries with exponential backoff + jitter
- Timeout values: per-agent with global maximum
- Failure modes: return structured error, no speculative outputs

### Schema Validation Strategy

**Validation Service Design:**
- **Hybrid validation:** Central request/response validation, per-agent step validation
- **Shared validation utility** used by all components
- **Rationale:** Centralized for consistency, per-agent for performance and isolation

**Schema Repair Mechanism:**
- **One-shot repair** via dedicated function using JSON Schema + validation errors
- **No full context in repair** - only schema and validation errors passed to repair function
- Repair prompt structure: JSON Schema + validation error details, strict "return valid JSON" instruction
- **Repair failure handling:** After repair attempt fails, return `SCHEMA_VALIDATION_FAILED` error with request_id

**Schema Versioning:**
- **Schema version tracked in PipelineState**
- **Backward compatible within /v1**, breaking changes via /v2
- Schema versions embedded in Pydantic model definitions or separate schema registry
- Schema evolution: maintain backward compatibility within major API version

**Validation Performance:**
- **Minimal perf work** - rely on Pydantic's native performance
- **Add metrics** for validation + repair success/failure rates
- Pre-compile validation schemas at startup if needed
- Monitor validation latency per step

### Authentication & Security

**API Key Storage:**
- **MVP:** Environment variable allowlist for API keys
- **Future:** Database/secrets manager for multi-tenant support
- Simple key validation against environment variable list

**Rate Limiting Implementation:**
- **Redis token-bucket per API key**
- **60 req/min, burst 20** (as specified in PRD)
- Use `slowapi` or custom Redis-backed middleware
- Per-API-key tracking in Redis for distributed rate limiting

**Input Sanitization:**
- **API-layer normalization** + strict schema + size limits + redaction
- **Pass structured subsets to agents** - only validated, sanitized data
- **No tool execution** - agents do not execute external tools or code
- Sanitization at API layer before pipeline execution

**Logging Strategy:**
- **Structured metadata only** - no raw input logging
- **Optional gated debug** with sanitization + hashing
- Structured logging with `request_id` correlation
- Log agent step outputs (structured) but not raw LLM prompts/responses
- Sanitized inputs in logs (redacted or hashed sensitive data)

### Infrastructure & Deployment

**Hosting Platform:**
- **Containerized FastAPI on managed platform** (Render/Fly/Railway)
- Platform choice: Render, Fly.io, or Railway (flexible)
- Serverless not suitable due to stateless but long-running agent pipeline

**Containerization:**
- **Docker multi-stage builds** with `python:3.11-slim` base image
- Optimize for image size and security
- Container orchestration: Platform-managed (no Kubernetes needed for MVP)

**Monitoring and Observability:**
- **Prometheus-style metrics** + structured logs
- Metrics: latency (P50, P95), error rate, schema failure rate, agent-level metrics
- Logging aggregation: Platform-managed logging or external service
- Agent-level metrics: Track per-agent execution time, success/failure rates
- Request_id correlation across all logs and metrics

**CI/CD:**
- **GitHub Actions CI/CD** with evaluation harness and staged promotion
- Pipeline stages: test (including eval harness), build, deploy
- Environment promotion: dev → staging → production
- Evaluation harness runs: small subset on PR, full suite nightly

**Environment Configuration:**
- **Env-based config** with pinned `logic_version` per environment
- **Secrets managed by platform** (Render/Fly/Railway secrets management)
- Configuration for prompt versions, feature flags, rate limits
- Environment separation: staging vs. production configurations

### Evaluation Harness

**Test Framework Structure:**
- **pytest + git-versioned golden cases** (folder-per-case)
- Golden decision test cases organized in `tests/golden/` directory
- Each golden case: folder with input, expected output, metadata
- Test data format: YAML or JSON for golden decisions

**Output Comparison:**
- **Structured comparison with hard gates** + invariant assertions
- **Avoid semantic similarity** - use exact or structured comparison
- Comparison metrics:
  - Schema validity (hard gate)
  - Determinism (same input → same output)
  - Invariant assertions (confidence ranges, bias detection, etc.)
- Handle acceptable differences vs. breaking changes explicitly

**Regression Testing:**
- **CI: small subset on PR**, full suite nightly
- Automated regression checks when prompt versions change
- **Failure criteria (regressions):**
  - Schema/contract breaks
  - Determinism breaks (same input → different output)
  - Invariant failures (confidence out of range, missing required fields)
  - Repair-rate spikes (indicates schema drift or prompt issues)

**Test Data Management:**
- **Git-versioned golden decisions** in repository
- Version golden decisions alongside logic versions
- Test data for different decision types (build vs. buy, vendor selection, etc.)
- Golden decisions organized by decision type and logic version

### Decision Impact Analysis

**Implementation Sequence:**

1. **Foundation Setup:**
   - FastAPI project structure initialization
   - Docker containerization setup
   - Basic CI/CD pipeline

2. **Core Pipeline:**
   - PipelineState definition
   - Agent orchestration engine
   - Basic agent implementations (stubs)

3. **LLM Integration:**
   - OpenAI SDK wrapper
   - Prompt template management
   - Async LLM call handling

4. **Schema Validation:**
   - Pydantic model definitions for all agents
   - Validation service implementation
   - Schema repair mechanism

5. **API Layer:**
   - FastAPI endpoints
   - Authentication middleware
   - Rate limiting implementation

6. **Observability:**
   - Metrics collection
   - Structured logging
   - Request_id correlation

7. **Evaluation Harness:**
   - Golden decision test suite
   - Regression testing framework
   - CI/CD integration

**Cross-Component Dependencies:**

- **Agent Orchestration** depends on: PipelineState, LLM Integration, Schema Validation
- **Schema Validation** depends on: Pydantic models, LLM Integration (for repair)
- **API Layer** depends on: Authentication, Rate Limiting, Agent Orchestration
- **Evaluation Harness** depends on: Agent Orchestration, Schema Validation
- **Observability** depends on: All components (cross-cutting concern)

**Technology Stack Summary:**

- **Language:** Python 3.11
- **Framework:** FastAPI
- **Validation:** Pydantic v2
- **LLM Client:** OpenAI SDK (wrapper for future abstraction)
- **Rate Limiting:** Redis + slowapi or custom middleware
- **Testing:** pytest + pytest-asyncio
- **Containerization:** Docker (multi-stage, python:3.11-slim)
- **Hosting:** Managed platform (Render/Fly/Railway)
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus-style metrics + structured logs
- **Database:** None in MVP (stateless design)

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
6 major areas where AI agents could make different choices: naming conventions, project structure, API formats, logging patterns, error handling, and validation timing.

### Naming Patterns

**API Endpoint Naming Conventions:**

- **RESTful plural resources:** `/v1/decisions/analyze`, `/v1/decisions/{decision_id}` (future)
- **Consistent versioning:** All endpoints under `/v1/` prefix
- **Action verbs in path:** Use verbs for actions (`/analyze`, `/replay`) when not standard REST verbs
- **Route parameters:** Use FastAPI path parameters `{decision_id}` not `:id` or query strings for resource identifiers
- **Query parameters:** Use `snake_case` for query parameters: `?logic_version=1.2.3`
- **Header naming:** Use standard HTTP headers; custom headers use `X-` prefix: `X-API-Key`, `X-Request-ID`

**Examples:**
- ✅ `/v1/decisions/analyze` (POST)
- ✅ `/v1/decisions/{decision_id}` (GET, future)
- ✅ `/v1/decisions/{decision_id}/replay` (POST, future)
- ✅ `/v1/meta` (GET)
- ✅ `/health` (GET, no version prefix for operational endpoints)
- ✅ `/ready` (GET, no version prefix for operational endpoints)

**Python Code Naming Conventions:**

- **Modules:** `snake_case.py` - `clarifier_agent.py`, `criteria_builder.py`, `pipeline_state.py`
- **Packages:** `snake_case/` - `app/agents/`, `app/orchestration/`, `app/validation/`
- **Classes:** `PascalCase` - `Clarifier`, `CriteriaBuilder`, `PipelineState`, `DecisionRequest`
- **Functions:** `snake_case()` - `process_decision()`, `validate_schema()`, `execute_agent()`
- **Variables:** `snake_case` - `pipeline_state`, `request_id`, `agent_output`
- **Constants:** `UPPER_SNAKE_CASE` - `MAX_RETRIES`, `DEFAULT_TIMEOUT`, `API_VERSION`
- **Private functions/variables:** `_leading_underscore` - `_validate_internal()`, `_cache_key`

**Agent Class Naming:**

- **Agent classes:** `PascalCase` without "Agent" suffix - `Clarifier`, `CriteriaBuilder`, `BiasChecker`, `OptionEvaluator`, `DecisionSynthesizer`
- **Rationale:** Context makes it clear these are agents; cleaner naming
- **Agent modules:** `snake_case` with descriptive names - `clarifier.py`, `criteria_builder.py`, `bias_checker.py`

**Schema/Model Naming:**

- **Pydantic models:** `PascalCase` with descriptive suffixes:
  - Request models: `DecisionRequest`, `ClarifierInput`
  - Response models: `DecisionResponse`, `ClarifierOutput`
  - State models: `PipelineState`, `AgentState`
  - Error models: `ErrorResponse`, `ValidationError`
- **Model fields:** `snake_case` - `request_id`, `confidence_score`, `bias_findings`
- **Enums:** `PascalCase` - `BiasType`, `DecisionStatus`, `ErrorCode`

**JSON Field Naming in API Responses:**

- **snake_case for all JSON fields:** `{"decision_id": "...", "confidence_score": 0.78, "bias_findings": [...]}`
- **Rationale:** Python-native, consistent with backend code, easier to map between Python objects and JSON
- **Exception:** If external API integration requires `camelCase`, use Pydantic `Field(alias="camelCase")` for serialization only

**File and Directory Naming:**

- **Test files:** `test_<module_name>.py` - `test_clarifier.py`, `test_pipeline.py`, `test_validation.py`
- **Test directories:** `tests/` for all tests, `tests/golden/` for golden decisions
- **Golden decision folders:** `tests/golden/decision_<type>_<id>/` - `tests/golden/decision_vendor_selection_001/`
- **Config files:** `config.py` or `settings.py` (single primary config file)
- **Environment files:** `.env.example`, `.env.local`, `.env.production` (not committed)
- **Documentation:** `README.md`, `docs/` directory for additional documentation

**Examples:**
- ✅ `app/agents/clarifier.py` (module)
- ✅ `app/agents/clarifier.py` → `class Clarifier` (class)
- ✅ `tests/test_clarifier.py` (test file)
- ✅ `tests/golden/decision_build_vs_buy_001/` (golden case folder)

### Structure Patterns

**Project Organization:**

- **Tests:** Separate `tests/` directory, not co-located
- **Test structure mirrors source:** `tests/app/agents/test_clarifier.py` mirrors `app/agents/clarifier.py`
- **Golden decisions:** `tests/golden/` with folder-per-case structure
- **Components organized by domain:** `app/agents/`, `app/orchestration/`, `app/validation/` (not by type)
- **Shared utilities:** `app/core/` for cross-cutting utilities (logging, config, exceptions)
- **Services:** `app/services/` for business logic services (if needed beyond agents)

**File Structure Patterns:**

- **One class per file:** Each agent in its own file (`clarifier.py`, `criteria_builder.py`)
- **Related models together:** Group related Pydantic models in same file (`app/schemas/decision.py`)
- **Config organization:** Single `app/core/config.py` with environment-based settings
- **Prompt templates:** `prompts/<logic_version>/<agent_name>.txt` or organized by version
- **Static assets:** Not applicable for API-only service (MVP)

**Directory Structure:**

```
decisionflow/
├── app/
│   ├── api/              # FastAPI routes and endpoints
│   │   ├── v1/
│   │   │   ├── decisions.py
│   │   │   └── meta.py
│   │   └── health.py
│   ├── agents/           # Agent implementations
│   │   ├── clarifier.py
│   │   ├── criteria_builder.py
│   │   ├── bias_checker.py
│   │   ├── option_evaluator.py
│   │   └── decision_synthesizer.py
│   ├── orchestration/    # Pipeline orchestration
│   │   ├── pipeline.py
│   │   └── runner.py
│   ├── schemas/          # Pydantic models
│   │   ├── decision.py
│   │   ├── agents.py
│   │   └── errors.py
│   ├── validation/       # Schema validation service
│   │   ├── service.py
│   │   └── repair.py
│   ├── evaluation/       # Evaluation harness
│   │   ├── harness.py
│   │   └── comparison.py
│   ├── core/             # Core utilities
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   └── llm/              # LLM integration
│       ├── client.py
│       └── prompts.py
├── tests/
│   ├── app/
│   │   └── agents/
│   │       └── test_clarifier.py
│   └── golden/
│       └── decision_<type>_<id>/
├── prompts/              # Prompt templates
│   └── v1.0.0/
│       ├── clarifier.txt
│       └── criteria_builder.txt
├── docs/
├── .github/
│   └── workflows/
├── Dockerfile
├── requirements.txt
└── README.md
```

### Format Patterns

**API Response Formats:**

- **Success responses:** Direct response object, no wrapper
  ```json
  {
    "decision": "Choose cloud provider",
    "options": [...],
    "winner": "AWS",
    "confidence": 0.78,
    "request_id": "req_123",
    "meta": {
      "api_version": "v1",
      "logic_version": "1.2.3",
      "schema_version": "1.0.0"
    }
  }
  ```
- **Error responses:** Standardized error envelope (as per PRD)
  ```json
  {
    "error": {
      "code": "SCHEMA_VALIDATION_FAILED",
      "message": "Agent output failed schema validation",
      "details": {...}
    },
    "request_id": "req_123"
  }
  ```
- **No data wrapper:** Do not use `{data: ..., error: ...}` wrapper pattern

**Data Exchange Formats:**

- **JSON field naming:** `snake_case` throughout
- **Date/time formats:** ISO 8601 strings - `"2025-12-23T10:00:00Z"`
- **Boolean values:** `true`/`false` (not `1`/`0`)
- **Null handling:** Use `null` (not empty strings or omitted fields)
- **Arrays:** Use arrays `[]` for lists, objects `{}` for single items
- **Numbers:** Use appropriate numeric types (integers for counts, floats for scores)

**Status Code Usage:**

- **200 OK:** Successful request
- **400 Bad Request:** Validation errors, invalid input
- **401 Unauthorized:** Invalid or missing API key
- **403 Forbidden:** API key lacks permissions
- **429 Too Many Requests:** Rate limit exceeded
- **500 Internal Server Error:** Unexpected server errors
- **503 Service Unavailable:** Dependency unavailable (model/tool unreachable)

### Communication Patterns

**Logging Formats:**

- **Structured logging:** JSON format for production, key-value pairs for development
- **Log levels:**
  - `DEBUG`: Detailed diagnostic information (agent step outputs, validation details)
  - `INFO`: General informational messages (request received, decision completed)
  - `WARNING`: Warning messages (schema repair attempted, retry occurred)
  - `ERROR`: Error conditions (validation failure, agent failure)
  - `CRITICAL`: Critical errors (system failure, dependency unavailable)
- **Request ID propagation:** Include `request_id` in all log entries
- **Structured fields:** `{"level": "INFO", "request_id": "req_123", "agent": "clarifier", "duration_ms": 150}`
- **No raw input logging:** Log structured metadata only, never raw user input or LLM prompts/responses

**Request ID Pattern:**

- **Generation:** UUID v4 at request entry point
- **Propagation:** Pass `request_id` through `PipelineState` to all components
- **Inclusion:** Include in all logs, metrics, and responses
- **Format:** `req_<uuid>` or just UUID - `req_550e8400-e29b-41d4-a716-446655440000`

**Agent Step Logging:**

- **Log structured agent outputs:** Log agent step results (typed data), not raw LLM responses
- **Log agent execution time:** Include duration for each agent step
- **Log validation results:** Log schema validation success/failure per step
- **No prompt/response logging:** Do not log raw LLM prompts or responses (security/privacy)

### Process Patterns

**Error Handling Patterns:**

- **Error boundaries:** Catch errors at API layer, transform to standardized error responses
- **Agent errors:** Agents raise typed exceptions, orchestration catches and handles
- **Validation errors:** Validation service raises `ValidationError`, caught by orchestration
- **LLM errors:** LLM client raises `LLMError`, caught by agent, transformed to agent error
- **Error transformation:** All errors transformed to `ErrorResponse` format before returning to client
- **Error logging:** Log errors with full context (request_id, agent, step) before transforming

**Retry Logic Patterns:**

- **Centralized retry:** Retry logic in LLM client wrapper, not in individual agents
- **Retry configuration:** Max 2 retries, exponential backoff + jitter, configurable per call type
- **Retry conditions:** Timeouts, transient 5xx errors, network errors
- **No retry for:** 4xx errors, schema validation failures, business logic errors
- **Retry logging:** Log retry attempts with `request_id` and attempt number

**Validation Timing:**

- **Request validation:** Validate request payload immediately on receipt (API layer)
- **Agent step validation:** Validate agent output immediately after agent execution (orchestration layer)
- **Response validation:** Validate final response before returning (API layer)
- **Validation service:** Centralized validation utility used by all validation points
- **Validation errors:** Fail fast with clear error messages, do not continue with invalid data

**Configuration Loading:**

- **Environment-based:** Load configuration from environment variables
- **Single config object:** `app/core/config.py` exports single `Settings` object (Pydantic BaseSettings)
- **Config access:** Import `settings` from config module, access as `settings.api_keys`
- **Secrets:** Load secrets from environment variables, never hardcode
- **Validation:** Validate configuration at startup, fail fast if invalid

### Enforcement Guidelines

**All AI Agents MUST:**

1. **Follow Python naming conventions:** `snake_case` for functions/variables/modules, `PascalCase` for classes
2. **Use consistent API endpoint naming:** RESTful plural resources under `/v1/` prefix
3. **Include request_id in all logs and responses:** Propagate `request_id` through entire request lifecycle
4. **Use standardized error format:** All errors must use `{error: {code, message, details}, request_id}` structure
5. **Validate at three points:** Request receipt, each agent step, response generation
6. **Log structured data only:** Never log raw user input or LLM prompts/responses
7. **Follow project structure:** Place files in correct directories according to established structure
8. **Use Pydantic models:** All data structures must be Pydantic models with `extra="forbid"`
9. **Include version metadata:** All responses must include `api_version`, `logic_version`, `schema_version` in meta
10. **Fail fast on errors:** Do not continue processing with invalid data or failed dependencies

**Pattern Enforcement:**

- **Code review:** Review for naming and structure consistency
- **Linting:** Use `ruff` or `black` for code formatting, `mypy` for type checking
- **Tests:** Golden decision tests enforce output format consistency
- **CI/CD:** Automated checks for naming conventions, structure, and format patterns
- **Documentation:** Document any exceptions to patterns with rationale

### Pattern Examples

**Good Examples:**

**API Endpoint:**
```python
@router.post("/v1/decisions/analyze")
async def analyze_decision(
    request: DecisionRequest,
    request_id: str = Header(..., alias="X-Request-ID")
) -> DecisionResponse:
    # Implementation
```

**Agent Class:**
```python
# app/agents/clarifier.py
class Clarifier:
    async def execute(self, state: PipelineState) -> ClarifierOutput:
        # Implementation
```

**Error Response:**
```python
{
    "error": {
        "code": "SCHEMA_VALIDATION_FAILED",
        "message": "Agent output failed schema validation",
        "details": {"agent": "criteria_builder", "errors": [...]}
    },
    "request_id": "req_550e8400-e29b-41d4-a716-446655440000"
}
```

**Logging:**
```python
logger.info(
    "Agent execution completed",
    extra={
        "request_id": state.request_id,
        "agent": "clarifier",
        "duration_ms": 150,
        "status": "success"
    }
)
```

**Anti-Patterns:**

❌ **Inconsistent naming:**
```python
# BAD: Mixing naming conventions
def processDecision():  # camelCase
    user_id = ...  # snake_case
```

✅ **Consistent naming:**
```python
# GOOD: Consistent snake_case
def process_decision():
    user_id = ...
```

❌ **Missing request_id:**
```python
# BAD: No request_id in logs
logger.info("Request processed")
```

✅ **Request_id included:**
```python
# GOOD: request_id in all logs
logger.info("Request processed", extra={"request_id": request_id})
```

❌ **Raw input logging:**
```python
# BAD: Logging raw user input
logger.info(f"User input: {raw_user_input}")
```

✅ **Structured metadata only:**
```python
# GOOD: Log structured metadata
logger.info("Request received", extra={"request_id": request_id, "input_size": len(input)})
```

## Project Structure & Boundaries

### Complete Project Directory Structure

```
decisionflow/
├── README.md
├── .gitignore
├── .env.example
├── .env.local                    # Local development (not committed)
├── pyproject.toml                # Python project config (poetry/uv)
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── Dockerfile                    # Multi-stage Docker build
├── docker-compose.yml            # Local development with Redis
├── .dockerignore
├── .github/
│   └── workflows/
│       ├── ci.yml                # CI pipeline with eval harness
│       └── deploy.yml            # Deployment workflow
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py       # FastAPI dependencies (auth, request_id)
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # API key authentication (FR33-FR34)
│   │   │   ├── rate_limit.py     # Rate limiting middleware (FR36, FR65-FR69)
│   │   │   └── request_id.py     # Request ID generation and propagation (FR39)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── decisions.py      # POST /v1/decisions/analyze (FR1, FR8-FR9)
│   │   │   └── meta.py            # GET /v1/meta (FR47-FR50, FR54)
│   │   ├── health.py             # GET /health (FR45)
│   │   └── ready.py              # GET /ready (FR46)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                # Base agent interface/abstract class
│   │   ├── clarifier.py           # Clarifier Agent (FR3)
│   │   ├── criteria_builder.py   # Criteria Builder Agent (FR4)
│   │   ├── bias_checker.py       # Bias Checker Agent (FR5, FR16-FR21)
│   │   ├── option_evaluator.py   # Option Evaluator Agent (FR6)
│   │   └── decision_synthesizer.py # Decision Synthesizer Agent (FR7, FR22-FR27)
│   ├── orchestration/
│   │   ├── __init__.py
│   │   ├── pipeline.py           # Deterministic pipeline execution (FR2, FR60-FR64)
│   │   ├── runner.py              # Pipeline runner/orchestrator
│   │   └── state.py               # PipelineState definition (request-scoped state)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── decision.py            # DecisionRequest, DecisionResponse (FR1, FR8-FR9)
│   │   ├── agents.py              # Agent input/output models (FR3-FR7)
│   │   │                           # ClarifierInput, ClarifierOutput, etc.
│   │   ├── errors.py              # ErrorResponse, error codes (FR38-FR44)
│   │   ├── state.py               # PipelineState Pydantic model
│   │   └── versioning.py          # Version metadata models (FR48-FR50, FR53)
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── service.py             # Centralized validation service (FR11-FR15)
│   │   ├── repair.py               # Schema repair mechanism (FR14)
│   │   └── schemas.py             # JSON Schema definitions for repair
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── harness.py             # Evaluation harness (FR55-FR59)
│   │   ├── comparison.py          # Output comparison across versions (FR56)
│   │   └── golden.py              # Golden decision test utilities
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py              # OpenAI SDK wrapper (provider-agnostic interface)
│   │   ├── prompts.py             # Prompt template loading and management
│   │   └── retry.py                # Retry logic with exponential backoff
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings/configuration (Pydantic BaseSettings)
│   │   ├── logging.py             # Structured logging setup
│   │   ├── exceptions.py          # Custom exception classes
│   │   ├── versioning.py          # Version management (API, logic, schema) (FR51-FR54)
│   │   └── sanitization.py        # Input sanitization (NFR18)
│   └── metrics/
│       ├── __init__.py
│       ├── collection.py          # Metrics collection (NFR46)
│       └── middleware.py          # Metrics middleware
├── prompts/
│   ├── README.md                  # Prompt versioning documentation
│   └── v1.0.0/                    # Logic version directory
│       ├── clarifier.txt
│       ├── criteria_builder.txt
│       ├── bias_checker.txt
│       ├── option_evaluator.txt
│       ├── decision_synthesizer.txt
│       └── repair.txt              # Schema repair prompt
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # pytest fixtures and configuration
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── test_decisions.py  # API endpoint tests
│   │   │   ├── test_health.py
│   │   │   └── test_meta.py
│   │   ├── agents/
│   │   │   ├── test_clarifier.py
│   │   │   ├── test_criteria_builder.py
│   │   │   ├── test_bias_checker.py
│   │   │   ├── test_option_evaluator.py
│   │   │   └── test_decision_synthesizer.py
│   │   ├── orchestration/
│   │   │   ├── test_pipeline.py
│   │   │   └── test_runner.py
│   │   ├── validation/
│   │   │   ├── test_service.py
│   │   │   └── test_repair.py
│   │   └── llm/
│   │       ├── test_client.py
│   │       └── test_retry.py
│   ├── golden/                    # Golden decision test cases
│   │   ├── decision_build_vs_buy_001/
│   │   │   ├── input.json
│   │   │   ├── expected_output.json
│   │   │   └── metadata.yaml
│   │   ├── decision_vendor_selection_001/
│   │   │   ├── input.json
│   │   │   ├── expected_output.json
│   │   │   └── metadata.yaml
│   │   └── README.md
│   └── integration/
│       ├── test_pipeline_integration.py
│       └── test_api_integration.py
├── docs/
│   ├── README.md
│   ├── api/                       # API documentation
│   │   └── openapi.json           # Auto-generated OpenAPI spec (FR70)
│   ├── architecture/              # Architecture documentation
│   └── development/               # Development guides
└── scripts/
    ├── generate_openapi.py        # Generate OpenAPI spec
    └── run_eval_harness.py        # Run evaluation harness
```

### Architectural Boundaries

**API Boundaries:**

- **External API Layer:** `app/api/` - All FastAPI routes and endpoints
  - Public endpoints: `/v1/decisions/analyze`, `/v1/meta`, `/health`, `/ready`
  - Authentication boundary: API key validation at middleware layer
  - Rate limiting boundary: Per-API-key rate limiting at middleware layer
  - Request validation boundary: Request payload validation at API layer

- **Internal Service Boundaries:**
  - **Orchestration Layer:** `app/orchestration/` - Coordinates agent execution
  - **Agent Layer:** `app/agents/` - Individual agent implementations
  - **Validation Layer:** `app/validation/` - Schema validation service
  - **LLM Layer:** `app/llm/` - LLM API client and prompt management

**Component Boundaries:**

- **Agent Interface:** All agents implement base agent interface (`app/agents/base.py`)
- **Pipeline State:** Single `PipelineState` object passed between agents (no direct agent-to-agent communication)
- **Validation Service:** Centralized validation used by API layer and orchestration layer
- **LLM Client:** Wrapper provides unified interface, agents do not call LLM directly

**Service Boundaries:**

- **Stateless Design:** No shared state between requests; all state in `PipelineState`
- **Agent Isolation:** Agents do not know about other agents; orchestration manages flow
- **Validation Isolation:** Validation service is independent, can be used by any component
- **LLM Abstraction:** LLM client provides abstraction; agents use structured interfaces

**Data Boundaries:**

- **No Persistence in MVP:** All data in-memory within request lifecycle
- **PipelineState:** Request-scoped state object, not persisted
- **Future Persistence:** If added, only final artifacts stored, not raw prompts/responses

### Requirements to Structure Mapping

**Feature/FR Category Mapping:**

**Decision Analysis Capabilities (FR1-FR10):**
- **Components:** `app/orchestration/pipeline.py`, `app/agents/*.py`
- **API Routes:** `app/api/v1/decisions.py`
- **Schemas:** `app/schemas/decision.py`, `app/schemas/agents.py`
- **Tests:** `tests/app/orchestration/`, `tests/app/agents/`

**Schema Validation & Data Integrity (FR11-FR15):**
- **Components:** `app/validation/service.py`, `app/validation/repair.py`
- **Integration:** Used by `app/api/` and `app/orchestration/`
- **Tests:** `tests/app/validation/`

**Bias Detection (FR16-FR21):**
- **Components:** `app/agents/bias_checker.py`
- **Schemas:** `app/schemas/agents.py` (BiasCheckerOutput)
- **Tests:** `tests/app/agents/test_bias_checker.py`

**Confidence Scoring (FR22-FR27):**
- **Components:** `app/agents/decision_synthesizer.py`
- **Schemas:** `app/schemas/agents.py` (DecisionSynthesizerOutput)
- **Tests:** `tests/app/agents/test_decision_synthesizer.py`

**Authentication & Authorization (FR33-FR37):**
- **Components:** `app/api/middleware/auth.py`, `app/core/config.py`
- **Integration:** FastAPI dependency injection
- **Tests:** `tests/app/api/test_auth.py`

**Error Handling & Diagnostics (FR38-FR44):**
- **Components:** `app/core/exceptions.py`, `app/schemas/errors.py`
- **Integration:** Error transformation at API layer
- **Tests:** `tests/app/api/` (error response tests)

**Operational Capabilities (FR45-FR50):**
- **Components:** `app/api/health.py`, `app/api/ready.py`, `app/api/v1/meta.py`
- **Tests:** `tests/app/api/test_health.py`, `tests/app/api/test_meta.py`

**Versioning Capabilities (FR51-FR54):**
- **Components:** `app/core/versioning.py`, `app/schemas/versioning.py`
- **Integration:** Version info included in all responses
- **Tests:** `tests/app/core/test_versioning.py`

**Evaluation & Testing (FR55-FR59):**
- **Components:** `app/evaluation/harness.py`, `app/evaluation/comparison.py`
- **Test Data:** `tests/golden/`
- **CI/CD:** `.github/workflows/ci.yml` runs evaluation harness

**Rate Limiting (FR65-FR69):**
- **Components:** `app/api/middleware/rate_limit.py`
- **Integration:** Redis-backed token bucket
- **Tests:** `tests/app/api/test_rate_limit.py`

**Cross-Cutting Concerns:**

**Observability:**
- **Logging:** `app/core/logging.py` - Structured logging setup
- **Metrics:** `app/metrics/collection.py` - Metrics collection
- **Request ID:** `app/api/middleware/request_id.py` - Request ID generation/propagation
- **Integration:** All components use structured logging with request_id

**Configuration:**
- **Config:** `app/core/config.py` - Single Settings object
- **Environment:** `.env.example`, `.env.local` - Environment variable management
- **Integration:** All components import settings from config module

**Security:**
- **Authentication:** `app/api/middleware/auth.py` - API key validation
- **Sanitization:** `app/core/sanitization.py` - Input sanitization
- **Integration:** Applied at API layer before pipeline execution

### Integration Points

**Internal Communication:**

- **API → Orchestration:** API endpoints call orchestration pipeline
- **Orchestration → Agents:** Pipeline runner calls agents in fixed order
- **Agents → LLM:** Agents call LLM client wrapper (not direct API calls)
- **Orchestration → Validation:** Pipeline validates agent outputs after each step
- **All → Logging:** All components use structured logging with request_id
- **All → Metrics:** All components emit metrics through metrics middleware

**External Integrations:**

- **LLM Provider:** OpenAI API (via `app/llm/client.py` wrapper)
- **Redis:** Rate limiting and token bucket storage
- **Monitoring:** Prometheus-style metrics endpoint (future)
- **CI/CD:** GitHub Actions for testing and deployment

**Data Flow:**

1. **Request Entry:** API endpoint receives request → Generate request_id → Validate API key → Rate limit check
2. **Request Validation:** Validate request payload against schema → Create PipelineState
3. **Pipeline Execution:** Orchestration runner executes agents sequentially:
   - Clarifier → Validate output → Update PipelineState
   - Criteria Builder → Validate output → Update PipelineState
   - Bias Checker → Validate output → Update PipelineState
   - Option Evaluator → Validate output → Update PipelineState
   - Decision Synthesizer → Validate output → Update PipelineState
4. **Response Generation:** Build DecisionResponse from PipelineState → Validate response schema → Return to client
5. **Error Handling:** Any error caught → Transform to ErrorResponse → Log with request_id → Return to client

### File Organization Patterns

**Configuration Files:**

- **Root level:** `pyproject.toml`, `requirements.txt`, `.env.example`
- **Application config:** `app/core/config.py` - Single source of truth for configuration
- **Environment files:** `.env.local` (local dev), `.env.production` (production, not committed)
- **Docker config:** `Dockerfile`, `docker-compose.yml`, `.dockerignore`

**Source Organization:**

- **Domain-based:** Organized by functional domain (agents, orchestration, validation)
- **One class per file:** Each agent in separate file, each major component in separate file
- **Shared utilities:** `app/core/` for cross-cutting concerns
- **API layer:** `app/api/` for all FastAPI routes and middleware

**Test Organization:**

- **Mirrors source structure:** `tests/app/` mirrors `app/` structure
- **Golden decisions:** `tests/golden/` with folder-per-case
- **Integration tests:** `tests/integration/` for end-to-end tests
- **Fixtures:** `tests/conftest.py` for shared pytest fixtures

**Prompt Organization:**

- **Version-based:** `prompts/<logic_version>/` - Each logic version has its own directory
- **Agent-specific:** Each agent has its own prompt file
- **Git-versioned:** Prompts committed to repository, versioned alongside code

### Development Workflow Integration

**Development Server Structure:**

- **Entry point:** `app/main.py` - FastAPI application initialization
- **Hot reload:** Uvicorn development server with auto-reload
- **Local dependencies:** `docker-compose.yml` for Redis (rate limiting)
- **Environment:** `.env.local` for local development configuration

**Build Process Structure:**

- **Docker build:** Multi-stage Dockerfile with `python:3.11-slim` base
- **Dependencies:** `requirements.txt` for production, `requirements-dev.txt` for development
- **Optimization:** Minimal image size, security scanning

**Deployment Structure:**

- **Container:** Single Docker container with FastAPI application
- **Platform:** Managed platform (Render/Fly/Railway) handles orchestration
- **Secrets:** Platform-managed secrets for API keys, LLM API keys
- **Environment:** Environment-based configuration with pinned logic_version

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**

All architectural decisions are compatible and work together:

- **Technology Stack:** Python 3.11, FastAPI, Pydantic v2, OpenAI SDK - all versions are compatible and production-ready
- **Async Support:** FastAPI's native async/await aligns with Python 3.11 async capabilities and LLM client async design
- **Validation Strategy:** Pydantic v2 provides both request/response validation and per-agent step validation with consistent schema enforcement
- **LLM Integration:** OpenAI SDK wrapper provides clean abstraction that supports both current OpenAI usage and future multi-provider extension
- **Infrastructure:** Docker containerization, managed platform hosting, and Redis for rate limiting are all compatible deployment patterns
- **No Conflicts:** All technology choices complement each other; no contradictory decisions identified

**Pattern Consistency:**

Implementation patterns consistently support architectural decisions:

- **Naming Conventions:** Python `snake_case` for code, RESTful plural for API endpoints, `snake_case` for JSON fields - all align with FastAPI and Python best practices
- **Structure Patterns:** Domain-based organization (agents, orchestration, validation) supports deterministic pipeline architecture and clear component boundaries
- **Communication Patterns:** Structured logging with `request_id`, standardized error formats, and Pydantic models ensure consistent data flow throughout the system
- **Process Patterns:** Fail-fast error handling, retry logic, and validation timing align with deterministic pipeline requirements and auditability goals

**Structure Alignment:**

Project structure fully supports all architectural decisions:

- **Deterministic Pipeline:** `app/orchestration/` and `app/agents/` structure enables fixed execution order and explicit contracts
- **Schema Validation:** `app/validation/` service supports validation at three critical points (request, agent steps, response)
- **Versioning:** `app/core/versioning.py` and `prompts/<logic_version>/` structure supports separate API, logic, and schema versioning
- **Evaluation Harness:** `app/evaluation/` and `tests/golden/` structure enables regression testing and output comparison
- **Integration Points:** Clear boundaries between API layer, orchestration, agents, validation, and LLM client support stateless design and testability

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:**

All 73 functional requirements are architecturally supported:

**Decision Analysis Capabilities (FR1-FR10):** ✅
- FR1: `app/api/v1/decisions.py` - POST /v1/decisions/analyze endpoint
- FR2: `app/orchestration/pipeline.py` - Deterministic multi-agent pipeline with fixed execution order
- FR3-FR7: `app/agents/*.py` - All 5 agents implemented with explicit contracts
- FR8-FR10: `app/schemas/decision.py` - Structured output with biases separated, machine-readable JSON

**Schema Validation & Data Integrity (FR11-FR15):** ✅
- FR11-FR13: `app/validation/service.py` - Validation at request, agent steps, and response
- FR14: `app/validation/repair.py` - Schema repair mechanism with one-shot repair
- FR15: Validation service guarantees schema validity of all responses

**Bias Detection Capabilities (FR16-FR21):** ✅
- FR16-FR19: `app/agents/bias_checker.py` - Four core bias types (sunk cost, confirmation, optimism, authority)
- FR20-FR21: `app/schemas/agents.py` - Bias findings in structured output, separated from recommendations

**Confidence Scoring Capabilities (FR22-FR27):** ✅
- FR22-FR26: `app/agents/decision_synthesizer.py` - Multi-factor confidence calculation
- FR27: `app/schemas/decision.py` - Confidence scores with breakdown in response

**Explainability Capabilities (FR28-FR32):** ✅
- FR28-FR31: All agents provide explicit justifications, weighted criteria, trade-offs, assumptions
- FR32: Structured explanations in `DecisionResponse` schema

**Authentication & Authorization (FR33-FR37):** ✅
- FR33-FR34: `app/api/middleware/auth.py` - API key authentication (Bearer token or X-API-Key header)
- FR35: `app/core/config.py` - Single-tenant MVP with API key scope
- FR36-FR37: `app/api/middleware/rate_limit.py` - Rate limiting per API key (60 req/min, burst 20)

**Error Handling & Diagnostics (FR38-FR44):** ✅
- FR38-FR39: `app/schemas/errors.py` - Standardized error envelopes with request_id
- FR40-FR44: `app/core/exceptions.py` - Typed error codes, retry-after information, validation/processing/system/rate limit errors

**Operational Capabilities (FR45-FR50):** ✅
- FR45: `app/api/health.py` - GET /health endpoint
- FR46: `app/api/ready.py` - GET /ready endpoint
- FR47-FR50: `app/api/v1/meta.py` - Version metadata endpoint and version reporting

**Versioning Capabilities (FR51-FR54):** ✅
- FR51: API versioning via `/v1/` URL path prefix
- FR52: Logic versioning via `prompts/<logic_version>/` directory structure
- FR53-FR54: `app/core/versioning.py` - Version information in responses and compatibility checking

**Evaluation & Testing Capabilities (FR55-FR59):** ✅
- FR55: `app/evaluation/harness.py` - Golden decision test suite
- FR56: `app/evaluation/comparison.py` - Output comparison across versions
- FR57-FR59: CI/CD integration with regression testing and testability demonstration

**Deterministic Execution, Rate Limiting, Documentation (FR60-FR73):** ✅
- FR60-FR64: `app/orchestration/pipeline.py` - Fixed agent order, explicit contracts, repeatable outputs, audit trails
- FR65-FR69: `app/api/middleware/rate_limit.py` - Rate limiting, token bucket, payload size limits
- FR70-FR73: FastAPI auto-generated OpenAPI spec, documentation structure in `docs/`

**Non-Functional Requirements Coverage:**

All 49 non-functional requirements are architecturally addressed:

**Performance (NFR1-NFR10):** ✅
- NFR1-NFR3: Async FastAPI, bounded concurrency, hard timeout 10s in orchestration
- NFR4-NFR5: Pydantic validation performance, minimal orchestration overhead
- NFR6-NFR7: Stateless design, async support for 50-100 concurrent requests
- NFR8-NFR10: Error handling with reduced confidence, latency warnings, complete responses only

**Security (NFR11-NFR22):** ✅
- NFR11-NFR14: HTTPS only, input sanitization, no raw input logging, encryption at rest (if persistence added)
- NFR15-NFR17: API key authentication, single-tenant MVP, future multi-tenant support
- NFR18-NFR20: `app/core/sanitization.py` - Input sanitization, structured logging only, secure key management
- NFR21-NFR22: GDPR-aware design (if persistence), no domain-specific compliance in MVP

**Scalability (NFR23-NFR30):** ✅
- NFR23-NFR26: Stateless API design, externalized configuration, horizontal scaling capability
- NFR27-NFR30: Rate limiting per API key, fail-fast with 429 responses, graceful degradation

**Integration (NFR31-NFR38):** ✅
- NFR31-NFR32: API-first, JSON-only, stable schemas via Pydantic models
- NFR33-NFR35: FastAPI auto-generated OpenAPI 3.0 spec, deterministic response structure, backward compatibility
- NFR36-NFR38: Typed error codes, explicit error messages, no ambiguous responses

**Reliability & Resilience (NFR39-NFR49):** ✅
- NFR39-NFR41: 99.5% uptime target, health/readiness endpoints
- NFR42-NFR44: Dependency failure handling with structured errors, no degraded decisions
- NFR45-NFR47: Request_id correlation, metrics collection, structured logging
- NFR48-NFR49: Platform-level incident treatment, clear error responses during downtime

### Implementation Readiness Validation ✅

**Decision Completeness:**

All critical architectural decisions are documented with sufficient detail:

- **Agent Orchestration:** Execution pattern, contract format, state management, output passing, error handling, determinism requirements - all fully specified
- **LLM Integration:** Client wrapper, async handling, prompt management, model selection, error handling - all decisions documented
- **Schema Validation:** Validation service design, repair mechanism, versioning, performance - comprehensive coverage
- **Authentication & Security:** API key storage, rate limiting, input sanitization, logging strategy - all decisions made
- **Infrastructure & Deployment:** Hosting platform, containerization, monitoring, CI/CD, environment configuration - complete specification
- **Evaluation Harness:** Test framework, output comparison, regression testing, test data management - fully defined

**Structure Completeness:**

Project structure is complete and specific:

- **All directories defined:** Complete directory tree with all files and subdirectories specified
- **Component boundaries clear:** API, orchestration, agents, validation, LLM, evaluation - all boundaries defined
- **Integration points specified:** Internal communication, external integrations, data flow - all documented
- **Test organization complete:** Unit tests, integration tests, golden decisions - all structured

**Pattern Completeness:**

Implementation patterns are comprehensive and enforceable:

- **Naming Patterns:** API endpoints, Python code, agents, schemas, JSON fields, files/directories - all conventions defined
- **Structure Patterns:** Project organization, file structure, directory structure - complete specification
- **Format Patterns:** API response formats, data exchange formats, status codes - all standardized
- **Communication Patterns:** Logging formats, request ID pattern, agent step logging - fully specified
- **Process Patterns:** Error handling, retry logic, validation timing, configuration loading - all patterns documented
- **Enforcement Guidelines:** 10 mandatory rules for AI agents, pattern enforcement mechanisms - clear and actionable

### Gap Analysis Results

**Critical Gaps:** None identified

All critical architectural decisions are complete and documented. No blocking gaps for implementation.

**Important Gaps (Non-Blocking):**

1. **Prompt Template Structure:** While prompt versioning is defined, specific prompt template format (few-shot examples, variable substitution) could be more detailed. However, this is implementation detail that can be refined during development.

2. **Metrics Endpoint:** Prometheus-style metrics are mentioned, but specific metrics endpoint path and format not specified. This is acceptable for MVP as metrics can be collected via platform-managed services.

3. **Schema Registry:** Schema versioning is defined, but explicit schema registry structure (if needed beyond Pydantic models) not detailed. Pydantic models may be sufficient for MVP.

4. **Multi-Provider LLM Abstraction:** Future extensibility is mentioned, but interface contract for multi-provider support not fully specified. This is intentionally deferred to post-MVP.

**Nice-to-Have Gaps:**

1. **Development Tooling:** Specific IDE configuration, debugging setup, local development workflow could be more detailed. These are developer experience improvements.

2. **Documentation Examples:** Code examples for common integration patterns could be added. These can be added during implementation.

3. **Performance Benchmarks:** Specific performance targets per agent step not defined. Overall pipeline targets (P50 ≤ 3s, P95 ≤ 5s) are sufficient for MVP.

4. **Monitoring Dashboards:** Specific dashboard structure and alerting rules not defined. Platform-managed monitoring may be sufficient for MVP.

### Validation Issues Addressed

**No Critical Issues Found**

The architecture is coherent, complete, and ready for implementation. All requirements are covered, all decisions are compatible, and all patterns are enforceable.

**Minor Recommendations (Optional):**

1. **Prompt Template Examples:** Consider adding example prompt templates during implementation to guide agent development
2. **Integration Test Scenarios:** Consider defining specific integration test scenarios beyond golden decisions
3. **Performance Profiling:** Consider adding performance profiling guidelines for agent optimization

These are implementation refinements, not architectural gaps.

### Architecture Completeness Checklist

**✅ Requirements Analysis**

- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**✅ Architectural Decisions**

- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**✅ Implementation Patterns**

- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**✅ Project Structure**

- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** ✅ **READY FOR IMPLEMENTATION**

**Confidence Level:** **HIGH** - All requirements are architecturally supported, all decisions are compatible, and all patterns are comprehensive and enforceable.

**Key Strengths:**

1. **Complete Requirements Coverage:** All 73 functional requirements and 49 non-functional requirements are architecturally supported with specific component mappings
2. **Coherent Technology Stack:** Python 3.11, FastAPI, Pydantic v2, OpenAI SDK - all compatible and production-ready
3. **Deterministic Architecture:** Fixed execution order, explicit contracts, schema validation at every step - core differentiator fully supported
4. **Comprehensive Patterns:** Naming, structure, format, communication, and process patterns are all defined with enforcement guidelines
5. **Clear Boundaries:** API, orchestration, agents, validation, LLM - all component boundaries clearly defined
6. **Evaluation Support:** Golden decision test suite, regression testing, output comparison - engineering maturity demonstrated
7. **Implementation Guidance:** Complete project structure, file organization, integration points - ready for AI agent implementation

**Areas for Future Enhancement:**

1. **Multi-Provider LLM Support:** Interface contract for extending beyond OpenAI (post-MVP)
2. **Decision Persistence:** Storage and replay endpoints (post-MVP)
3. **Advanced Analytics:** Dashboard and analytics capabilities (post-MVP)
4. **Multi-Tenant Support:** Database-backed API keys and tenant isolation (post-MVP)
5. **Performance Optimization:** Agent-level performance profiling and optimization (post-MVP)

### Implementation Handoff

**AI Agent Guidelines:**

- Follow all architectural decisions exactly as documented in this document
- Use implementation patterns consistently across all components (naming, structure, format, communication, process)
- Respect project structure and boundaries - place files in correct directories according to established structure
- Refer to this document for all architectural questions - all decisions are documented here
- Enforce consistency rules - use the 10 mandatory rules for AI agents defined in Implementation Patterns section

**First Implementation Priority:**

1. **Initialize Project Structure:** Create the complete directory structure as defined in "Project Structure & Boundaries" section
2. **Set Up FastAPI Application:** Initialize FastAPI app with basic configuration (`app/main.py`, `app/core/config.py`)
3. **Define Core Schemas:** Create Pydantic models for `DecisionRequest`, `DecisionResponse`, `PipelineState` (`app/schemas/`)
4. **Implement Pipeline State:** Create `PipelineState` model and basic orchestration structure (`app/orchestration/state.py`, `app/orchestration/pipeline.py`)
5. **Set Up LLM Client:** Implement OpenAI SDK wrapper with retry logic (`app/llm/client.py`, `app/llm/retry.py`)
6. **Create Agent Base:** Define base agent interface (`app/agents/base.py`)
7. **Implement First Agent:** Create Clarifier Agent as proof of concept (`app/agents/clarifier.py`)
8. **Set Up Validation Service:** Implement validation service with schema repair (`app/validation/service.py`, `app/validation/repair.py`)
9. **Create API Endpoint:** Implement POST /v1/decisions/analyze endpoint (`app/api/v1/decisions.py`)
10. **Add Authentication:** Implement API key authentication middleware (`app/api/middleware/auth.py`)

**Implementation Sequence:**

Follow the "Decision Impact Analysis" section for detailed implementation sequence. Start with foundation setup, then core pipeline, then LLM integration, then schema validation, then API layer, then observability, then evaluation harness.

**Success Criteria:**

- All 73 functional requirements implemented and tested
- All 49 non-functional requirements met
- Deterministic pipeline produces repeatable outputs
- Schema validation passes at all three points (request, agent steps, response)
- Evaluation harness supports regression testing
- All implementation patterns consistently applied

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅
**Total Steps Completed:** 8
**Date Completed:** 2025-12-23
**Document Location:** `_bmad-output/architecture.md`

### Final Architecture Deliverables

**📋 Complete Architecture Document**

- All architectural decisions documented with specific versions
- Implementation patterns ensuring AI agent consistency
- Complete project structure with all files and directories
- Requirements to architecture mapping
- Validation confirming coherence and completeness

**🏗️ Implementation Ready Foundation**

- **6 major architectural decision categories** made:
  1. Agent Orchestration Architecture
  2. LLM Integration
  3. Schema Validation Strategy
  4. Authentication & Security
  5. Infrastructure & Deployment
  6. Evaluation Harness
- **5 implementation pattern categories** defined:
  1. Naming Patterns
  2. Structure Patterns
  3. Format Patterns
  4. Communication Patterns
  5. Process Patterns
- **6 architectural components** specified:
  1. API Layer
  2. Orchestration Layer
  3. Agent Layer
  4. Validation Layer
  5. LLM Layer
  6. Evaluation Layer
- **122 requirements** fully supported:
  - 73 functional requirements
  - 49 non-functional requirements

**📚 AI Agent Implementation Guide**

- Technology stack with verified versions (Python 3.11, FastAPI, Pydantic v2, OpenAI SDK)
- Consistency rules that prevent implementation conflicts (10 mandatory rules)
- Project structure with clear boundaries (complete directory tree)
- Integration patterns and communication standards (structured logging, error handling, validation)

### Implementation Handoff

**For AI Agents:**
This architecture document is your complete guide for implementing DecisionFlow. Follow all decisions, patterns, and structures exactly as documented.

**First Implementation Priority:**

1. **Initialize Project Structure:** Create the complete directory structure as defined in "Project Structure & Boundaries" section
2. **Set Up FastAPI Application:** Initialize FastAPI app with basic configuration (`app/main.py`, `app/core/config.py`)
3. **Define Core Schemas:** Create Pydantic models for `DecisionRequest`, `DecisionResponse`, `PipelineState` (`app/schemas/`)
4. **Implement Pipeline State:** Create `PipelineState` model and basic orchestration structure (`app/orchestration/state.py`, `app/orchestration/pipeline.py`)
5. **Set Up LLM Client:** Implement OpenAI SDK wrapper with retry logic (`app/llm/client.py`, `app/llm/retry.py`)
6. **Create Agent Base:** Define base agent interface (`app/agents/base.py`)
7. **Implement First Agent:** Create Clarifier Agent as proof of concept (`app/agents/clarifier.py`)
8. **Set Up Validation Service:** Implement validation service with schema repair (`app/validation/service.py`, `app/validation/repair.py`)
9. **Create API Endpoint:** Implement POST /v1/decisions/analyze endpoint (`app/api/v1/decisions.py`)
10. **Add Authentication:** Implement API key authentication middleware (`app/api/middleware/auth.py`)

**Development Sequence:**

1. Initialize project using documented starter template (custom FastAPI structure)
2. Set up development environment per architecture (Python 3.11, FastAPI, dependencies)
3. Implement core architectural foundations (PipelineState, base agent interface, LLM client)
4. Build features following established patterns (agents, orchestration, validation)
5. Maintain consistency with documented rules (naming, structure, format, communication, process)

### Quality Assurance Checklist

**✅ Architecture Coherence**

- [x] All decisions work together without conflicts
- [x] Technology choices are compatible
- [x] Patterns support the architectural decisions
- [x] Structure aligns with all choices

**✅ Requirements Coverage**

- [x] All functional requirements are supported
- [x] All non-functional requirements are addressed
- [x] Cross-cutting concerns are handled
- [x] Integration points are defined

**✅ Implementation Readiness**

- [x] Decisions are specific and actionable
- [x] Patterns prevent agent conflicts
- [x] Structure is complete and unambiguous
- [x] Examples are provided for clarity

### Project Success Factors

**🎯 Clear Decision Framework**
Every technology choice was made collaboratively with clear rationale, ensuring all stakeholders understand the architectural direction. The deterministic multi-agent pipeline architecture is the core differentiator, fully supported by all architectural decisions.

**🔧 Consistency Guarantee**
Implementation patterns and rules ensure that multiple AI agents will produce compatible, consistent code that works together seamlessly. The 10 mandatory rules for AI agents provide clear enforcement guidelines.

**📋 Complete Coverage**
All project requirements are architecturally supported, with clear mapping from business needs to technical implementation. All 73 functional requirements and 49 non-functional requirements have specific component mappings.

**🏗️ Solid Foundation**
The chosen custom FastAPI structure and architectural patterns provide a production-ready foundation following current best practices. The deterministic pipeline architecture enables testability, debuggability, and auditability.

---

**Architecture Status:** READY FOR IMPLEMENTATION ✅

**Next Phase:** Begin implementation using the architectural decisions and patterns documented herein.

**Document Maintenance:** Update this architecture when major technical decisions are made during implementation.

