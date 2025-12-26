---
stepsCompleted: [1, 2, 3, 4]
inputDocuments: ['_bmad-output/prd.md', '_bmad-output/architecture.md']
status: 'complete'
completedAt: '2025-12-23'
---

# DesicionFlow - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for DesicionFlow, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: API consumers can submit decision requests with context, options, and constraints via POST /v1/decisions/analyze

FR2: The system can process decision requests through a deterministic multi-agent pipeline with fixed execution order

FR3: The system can execute the Clarifier Agent to identify missing inputs and ask essential questions

FR4: The system can execute the Criteria Builder Agent to convert vague goals into weighted evaluation criteria

FR5: The system can execute the Bias Checker Agent to detect and name specific cognitive biases (sunk cost, confirmation, optimism, authority)

FR6: The system can execute the Option Evaluator Agent to score each option against criteria with explicit justifications

FR7: The system can execute the Decision Synthesizer Agent to produce final recommendation with confidence score

FR8: API consumers can receive structured decision analysis with weighted criteria, trade-offs, explicit biases, confidence scores, and assumptions

FR9: API consumers can receive machine-readable JSON outputs designed for service consumption

FR10: The system can return bias findings separated from final recommendations in structured output

FR11: The system can validate request payloads against defined JSON Schema before processing

FR12: The system can validate agent outputs against defined schemas at every pipeline step

FR13: The system can validate response payloads against defined schema before returning to clients

FR14: The system can attempt schema repair when agent outputs fail validation before failing with error

FR15: The system can guarantee schema validity of all responses returned to API consumers

FR16: The system can detect sunk cost bias in decision inputs and criteria

FR17: The system can detect confirmation bias in decision inputs and criteria

FR18: The system can detect optimism bias in decision inputs and criteria

FR19: The system can detect authority bias in decision inputs and criteria

FR20: The system can return detected biases with names and descriptions in structured output

FR21: The system can separate bias findings from final recommendations in output

FR22: The system can calculate confidence scores based on input completeness

FR23: The system can calculate confidence scores based on agent agreement

FR24: The system can calculate confidence scores based on evidence strength

FR25: The system can incorporate detected biases into confidence score calculation

FR26: The system can document assumptions that affect confidence scores

FR27: API consumers can receive confidence scores with breakdown of contributing factors

FR28: The system can provide explicit justifications for each option score

FR29: The system can provide weighted criteria with normalized scores in output

FR30: The system can provide trade-off analysis between options in output

FR31: The system can provide assumptions documented in structured output

FR32: API consumers can understand the reasoning behind recommendations through structured explanations

FR33: API consumers can authenticate using API keys via Bearer token or X-API-Key header

FR34: The system can validate API keys before processing requests

FR35: The system can associate API keys with project scope (single-tenant MVP)

FR36: The system can enforce rate limits per API key (60 req/min, burst up to 20)

FR37: API consumers can receive rate limit information in response headers

FR38: The system can return standardized error envelopes with error code, message, details, and request_id

FR39: API consumers can receive request_id in all responses for correlation and debugging

FR40: The system can return validation errors when request payloads fail schema validation

FR41: The system can return processing errors when agent pipeline execution fails

FR42: The system can return system errors when dependencies are unavailable

FR43: The system can return rate limit errors when request limits are exceeded

FR44: API consumers can receive retry-after information when rate limits are exceeded

FR45: Orchestration systems can check service liveness via GET /health endpoint

FR46: Orchestration systems can check service readiness via GET /ready endpoint (verifies model/tool dependencies)

FR47: API consumers can retrieve service metadata (service version, logic version, schema version, build hash) via GET /v1/meta

FR48: The system can report service version in metadata

FR49: The system can report logic version (prompt bundle version) in metadata

FR50: The system can report schema version in metadata and responses

FR51: The system can support API versioning via URL path (/v1/...)

FR52: The system can maintain separate logic versioning independent of API version

FR53: The system can include version information (API, logic, schema) in responses

FR54: API consumers can check version compatibility via /v1/meta endpoint

FR55: The system can support golden decision test suite for regression testing

FR56: The system can compare outputs across different logic versions

FR57: The system can perform regression checks on prompt version changes

FR58: The system can demonstrate testability through evaluation harness

FR59: The system can demonstrate auditability through structured outputs and versioning

FR60: The system can execute agents in fixed order (Clarifier → Criteria Builder → Bias Checker → Option Evaluator → Decision Synthesizer)

FR61: The system can enforce explicit contracts for each agent in the pipeline

FR62: The system can produce repeatable outputs for the same input

FR63: The system can provide audit trails through agent step outputs

FR64: The system can support debugging through structured agent outputs at each step

FR65: The system can enforce rate limits per API key

FR66: The system can support token bucket algorithm for burst allowance

FR67: The system can enforce payload size limits (max 256KB request size)

FR68: The system can enforce option and criteria count limits to bound processing costs

FR69: The system can optionally enforce IP-based rate limiting as secondary protection

FR70: API consumers can access OpenAPI 3.0 specification for all endpoints

FR71: API consumers can access code samples (cURL, Python, Node.js) for integration

FR72: API consumers can access integration guides and best practices

FR73: API consumers can access error handling examples and troubleshooting guides

### NonFunctional Requirements

NFR1: POST /v1/decisions/analyze endpoint must complete within 3 seconds for 50% of requests (P50 ≤ 3s)

NFR2: POST /v1/decisions/analyze endpoint must complete within 5 seconds for 95% of requests (P95 ≤ 5s)

NFR3: POST /v1/decisions/analyze endpoint must have a hard timeout of 10 seconds, after which the request is terminated

NFR4: Schema validation must not add unpredictable latency to request processing

NFR5: Agent orchestration must not add unpredictable latency to request processing

NFR6: The system must support 50-100 concurrent requests in MVP

NFR7: Requests must be independent and stateless to enable horizontal scaling

NFR8: If response time exceeds targets, the system must return structured response with reduced confidence score

NFR9: If response time exceeds targets, the system must include explicit latency warning in response

NFR10: The system must not return partial or streaming outputs in MVP (complete responses only)

NFR11: The system must protect decision context data which may include strategic, internal, or sensitive business information

NFR12: The system must protect API credentials (API keys)

NFR13: All data transmission must use HTTPS only (no unencrypted HTTP)

NFR14: If decision persistence is enabled, stored data must be encrypted at rest

NFR15: The system must use API-key-based authentication for all requests

NFR16: The system must support single-tenant MVP with per-project API key scope

NFR17: The system must support per-tenant isolation as a future capability (not required in MVP)

NFR18: The system must sanitize inputs to prevent prompt injection attacks

NFR19: The system must not log raw input data by default to prevent accidental exposure of sensitive information

NFR20: The system must prevent credential leakage through secure key management

NFR21: The system must be GDPR-aware if decision data is stored (support opt-out logging and deletion)

NFR22: The system must not require domain-specific compliance (HIPAA, PCI-DSS) in MVP

NFR23: The system must support low to moderate traffic for early adopters and internal tools in MVP

NFR24: The system must be designed for horizontal scaling through stateless API architecture

NFR25: The system must use stateless API design to enable horizontal scaling

NFR26: The system must externalize configuration to support scaling without code changes

NFR27: The system must implement rate limiting per API key (MVP baseline: 60 req/min)

NFR28: If capacity is exceeded, the system must fail fast with clear 429 (Rate Limit Exceeded) responses

NFR29: The system must not silently degrade when capacity is exceeded

NFR30: The system must support graceful degradation through rate limiting rather than service failure

NFR31: The system must be API-first with JSON-only data format

NFR32: The system must provide stable schemas as a hard requirement for integration reliability

NFR33: The system must provide complete OpenAPI 3.0 specification for all endpoints

NFR34: The system must provide deterministic response structure for all endpoints

NFR35: The system must maintain backward compatibility within /v1 API version

NFR36: Integration failures must be explicit with typed error codes (no ambiguous responses)

NFR37: The system must not return partial or ambiguous responses that could cause integration failures

NFR38: The system must provide clear error messages that enable integration debugging

NFR39: The system must achieve 99.5% uptime in MVP

NFR40: The system must provide clear health endpoints (GET /health) for liveness checks

NFR41: The system must provide clear readiness endpoints (GET /ready) for dependency verification

NFR42: If model/tool dependency fails, the system must return structured error response

NFR43: If model/tool dependency fails, the system must not return degraded or speculative decisions

NFR44: The system must clearly indicate dependency failures in error responses

NFR45: The system must include request_id on every response for correlation and debugging

NFR46: The system must provide basic metrics: latency (P50, P95), error rate, schema failure rate

NFR47: The system must enable observability through structured logging with request_id correlation

NFR48: System downtime blocks decision workflows and is treated as platform-level incident, not best-effort service

NFR49: The system must provide clear error responses during downtime to enable client-side handling

### Additional Requirements

- **Starter Template:** Custom FastAPI structure (not a pre-built template) - Project initialization should be the FIRST implementation story (Epic 1 Story 1)
- **Infrastructure:** Containerized FastAPI on managed platform (Render/Fly/Railway), Docker multi-stage builds with python:3.11-slim
- **LLM Integration:** OpenAI SDK wrapper with bounded concurrency, strict timeouts, max 2 retries with exponential backoff
- **Prompt Management:** Git-versioned prompt bundles per logic_version, stored in prompts/<logic_version>/ directory
- **Schema Validation:** Hybrid validation (central request/response, per-agent step) with one-shot repair mechanism
- **Authentication:** API keys via environment allowlist for MVP (database/secrets manager later for multi-tenant)
- **Rate Limiting:** Redis token-bucket per API key (60 req/min, burst 20)
- **Monitoring:** Prometheus-style metrics + structured logs with request_id correlation
- **CI/CD:** GitHub Actions with evaluation harness and staged promotion
- **Testing:** pytest + pytest-asyncio, golden decision test suite in tests/golden/ with folder-per-case structure
- **Versioning:** Separate API versioning (/v1/...), logic versioning (prompt bundle), and schema versioning with compatibility checks
- **Project Structure:** Complete directory structure defined in architecture with clear component boundaries (API, orchestration, agents, validation, LLM, evaluation)
- **Deterministic Pipeline:** Fixed execution order (Clarifier → Criteria Builder → Bias Checker → Option Evaluator → Decision Synthesizer) with explicit contracts per agent
- **PipelineState:** Request-scoped state object (Pydantic model) containing request_id, versions, normalized input, agent outputs, derived artifacts
- **Error Handling:** Fail-fast by default, standardized error envelopes with request_id, typed error codes
- **Input Sanitization:** API-layer normalization + strict schema + size limits + redaction, pass structured subsets to agents
- **Logging:** Structured metadata only, no raw input logging, request_id in all logs
- **Configuration:** Environment-based config with pinned logic_version per environment, single Settings object from app/core/config.py

### FR Coverage Map

FR1: Epic 2 - Submit decision requests via POST /v1/decisions/analyze
FR2: Epic 2 - Process requests through deterministic multi-agent pipeline
FR3: Epic 2 - Execute Clarifier Agent
FR4: Epic 2 - Execute Criteria Builder Agent
FR5: Epic 2 - Execute Bias Checker Agent
FR6: Epic 2 - Execute Option Evaluator Agent
FR7: Epic 2 - Execute Decision Synthesizer Agent
FR8: Epic 2 - Receive structured decision analysis with all components
FR9: Epic 2 - Receive machine-readable JSON outputs
FR10: Epic 2 - Return bias findings separated from recommendations
FR11: Epic 2 - Validate request payloads against JSON Schema
FR12: Epic 2 - Validate agent outputs at every pipeline step
FR13: Epic 2 - Validate response payloads before returning
FR14: Epic 2 - Attempt schema repair on validation failure
FR15: Epic 2 - Guarantee schema validity of all responses
FR16: Epic 2 - Detect sunk cost bias
FR17: Epic 2 - Detect confirmation bias
FR18: Epic 2 - Detect optimism bias
FR19: Epic 2 - Detect authority bias
FR20: Epic 2 - Return detected biases with names and descriptions
FR21: Epic 2 - Separate bias findings from recommendations
FR22: Epic 2 - Calculate confidence scores based on input completeness
FR23: Epic 2 - Calculate confidence scores based on agent agreement
FR24: Epic 2 - Calculate confidence scores based on evidence strength
FR25: Epic 2 - Incorporate detected biases into confidence calculation
FR26: Epic 2 - Document assumptions affecting confidence scores
FR27: Epic 2 - Receive confidence scores with breakdown
FR28: Epic 2 - Provide explicit justifications for option scores
FR29: Epic 2 - Provide weighted criteria with normalized scores
FR30: Epic 2 - Provide trade-off analysis between options
FR31: Epic 2 - Provide assumptions in structured output
FR32: Epic 2 - Understand reasoning through structured explanations
FR33: Epic 3 - Authenticate using API keys via Bearer token or X-API-Key header
FR34: Epic 3 - Validate API keys before processing
FR35: Epic 3 - Associate API keys with project scope
FR36: Epic 3 - Enforce rate limits per API key (60 req/min, burst 20)
FR37: Epic 3 - Receive rate limit information in response headers
FR38: Epic 2 - Return standardized error envelopes with error code, message, details, request_id
FR39: Epic 2 - Receive request_id in all responses
FR40: Epic 2 - Return validation errors when payloads fail schema validation
FR41: Epic 2 - Return processing errors when agent pipeline fails
FR42: Epic 2 - Return system errors when dependencies unavailable
FR43: Epic 3 - Return rate limit errors when limits exceeded
FR44: Epic 3 - Receive retry-after information when rate limits exceeded
FR45: Epic 4 - Check service liveness via GET /health endpoint
FR46: Epic 4 - Check service readiness via GET /ready endpoint
FR47: Epic 4 - Retrieve service metadata via GET /v1/meta
FR48: Epic 4 - Report service version in metadata
FR49: Epic 4 - Report logic version in metadata
FR50: Epic 4 - Report schema version in metadata and responses
FR51: Epic 4 - Support API versioning via URL path (/v1/...)
FR52: Epic 4 - Maintain separate logic versioning independent of API version
FR53: Epic 4 - Include version information (API, logic, schema) in responses
FR54: Epic 4 - Check version compatibility via /v1/meta endpoint
FR55: Epic 5 - Support golden decision test suite for regression testing
FR56: Epic 5 - Compare outputs across different logic versions
FR57: Epic 5 - Perform regression checks on prompt version changes
FR58: Epic 5 - Demonstrate testability through evaluation harness
FR59: Epic 5 - Demonstrate auditability through structured outputs and versioning
FR60: Epic 2 - Execute agents in fixed order
FR61: Epic 2 - Enforce explicit contracts for each agent
FR62: Epic 2 - Produce repeatable outputs for same input
FR63: Epic 2 - Provide audit trails through agent step outputs
FR64: Epic 2 - Support debugging through structured agent outputs
FR65: Epic 3 - Enforce rate limits per API key
FR66: Epic 3 - Support token bucket algorithm for burst allowance
FR67: Epic 3 - Enforce payload size limits (max 256KB)
FR68: Epic 3 - Enforce option and criteria count limits
FR69: Epic 3 - Optionally enforce IP-based rate limiting
FR70: Epic 5 - Access OpenAPI 3.0 specification for all endpoints
FR71: Epic 5 - Access code samples (cURL, Python, Node.js) for integration
FR72: Epic 5 - Access integration guides and best practices
FR73: Epic 5 - Access error handling examples and troubleshooting guides

## Epic List

### Epic 1: Project Foundation & Infrastructure Setup

**Epic Goal:** Developers have a working project structure, development environment, and deployment infrastructure that enables all future development work.

**User Outcome:** Development team can set up the project locally, run tests, build Docker containers, and deploy to a managed platform. The foundation supports the deterministic multi-agent pipeline architecture.

**FRs covered:** Project initialization (from Architecture requirements), infrastructure setup, Docker containerization, CI/CD pipeline basics

**Implementation Notes:**
- Custom FastAPI structure (not pre-built template) as specified in Architecture
- Complete directory structure from architecture document
- Docker multi-stage builds with python:3.11-slim
- GitHub Actions CI/CD pipeline
- Development environment setup (Redis for rate limiting, environment configuration)
- Project structure optimized for deterministic agent pipeline architecture

### Epic 2: Core Decision Analysis Pipeline

**Epic Goal:** API consumers can submit decision requests and receive structured, bias-aware, explainable recommendations through a deterministic multi-agent pipeline.

**User Outcome:** Users can POST decision requests to /v1/decisions/analyze and receive machine-readable JSON responses containing weighted criteria, trade-offs, explicit bias detections, confidence scores, and clear recommendations. The system processes requests through a fixed-order agent pipeline (Clarifier → Criteria Builder → Bias Checker → Option Evaluator → Decision Synthesizer) with schema validation at every step.

**FRs covered:** FR1-FR10 (Decision Analysis), FR11-FR15 (Schema Validation), FR16-FR21 (Bias Detection), FR22-FR27 (Confidence Scoring), FR28-FR32 (Explainability), FR38-FR44 (Error Handling - except rate limit), FR60-FR64 (Deterministic Execution)

**Implementation Notes:**
- All 5 agents must be implemented with explicit Pydantic contracts
- Schema validation at three points: request, each agent step, response
- Schema repair mechanism with one-shot attempt
- PipelineState (Pydantic model) for request-scoped state management
- LLM integration with OpenAI SDK wrapper, bounded concurrency, retry logic
- Prompt templates in prompts/<logic_version>/ directory
- Structured error responses with request_id
- Deterministic execution with low temperature and fixed agent order

### Epic 3: Security & Access Control

**Epic Goal:** API consumers can securely authenticate and use the API with appropriate rate limiting and protection mechanisms.

**User Outcome:** Users authenticate using API keys (Bearer token or X-API-Key header), receive rate limit information in responses, and are protected from abuse through token-bucket rate limiting. Inputs are sanitized to prevent prompt injection attacks.

**FRs covered:** FR33-FR37 (Authentication & Authorization), FR43-FR44 (Rate Limit Errors), FR65-FR69 (Rate Limiting & Protection)

**Implementation Notes:**
- API key authentication via environment allowlist (MVP)
- Redis token-bucket rate limiting (60 req/min, burst 20)
- Input sanitization at API layer before pipeline execution
- Payload size limits (max 256KB)
- Option and criteria count limits to bound processing costs
- Rate limit headers in responses (X-RateLimit-*)

### Epic 4: Observability & Operations

**Epic Goal:** Operators can monitor system health, check versions, debug issues, and understand system behavior through structured logging and metrics.

**User Outcome:** Operators can check service liveness (/health), verify readiness (/ready), retrieve version metadata (/v1/meta), and correlate logs and metrics using request_id. System provides structured logging with request_id correlation and basic metrics (latency P50/P95, error rate, schema failure rate).

**FRs covered:** FR45-FR50 (Operational Capabilities), FR51-FR54 (Versioning Capabilities)

**Implementation Notes:**
- Health endpoint for liveness checks
- Readiness endpoint verifying model/tool dependencies
- Version metadata endpoint with API, logic, and schema versions
- Structured logging with request_id in all entries
- Prometheus-style metrics collection
- No raw input logging (security/privacy)
- Version information in all responses (meta field)

### Epic 5: Quality Assurance & Testing

**Epic Goal:** Developers and operators can validate system correctness, perform regression testing, and access comprehensive documentation for integration.

**User Outcome:** Developers can run golden decision test suite for regression testing, compare outputs across logic versions, and validate prompt changes. API consumers can access OpenAPI 3.0 specification, code samples, integration guides, and error handling examples.

**FRs covered:** FR55-FR59 (Evaluation & Testing), FR70-FR73 (Documentation & Integration)

**Implementation Notes:**
- Golden decision test suite in tests/golden/ with folder-per-case structure
- Evaluation harness for regression testing across prompt versions
- Output comparison across logic versions
- FastAPI auto-generated OpenAPI 3.0 specification
- Integration documentation and code samples
- CI/CD integration with evaluation harness (small subset on PR, full suite nightly)

## Epic 1: Project Foundation & Infrastructure Setup

**Epic Goal:** Developers have a working project structure, development environment, and deployment infrastructure that enables all future development work.

**User Outcome:** Development team can set up the project locally, run tests, build Docker containers, and deploy to a managed platform. The foundation supports the deterministic multi-agent pipeline architecture.

### Story 1.1: Initialize Project Structure

As a developer,
I want the complete project directory structure with all required files and folders,
So that I have a foundation for implementing the deterministic multi-agent pipeline architecture.

**Acceptance Criteria:**

**Given** the architecture document specifies a custom FastAPI structure
**When** I initialize the project
**Then** all directories from the architecture document are created (app/, tests/, prompts/, docs/, scripts/, .github/workflows/)
**And** all __init__.py files are created in Python packages
**And** basic configuration files are created (.gitignore, .env.example, pyproject.toml, requirements.txt, requirements-dev.txt)
**And** README.md is created with project overview
**And** the structure matches the architecture document exactly

### Story 1.2: Set Up Development Environment

As a developer,
I want a configured local development environment with dependencies and Redis,
So that I can run the application locally and develop features.

**Acceptance Criteria:**

**Given** the project structure is initialized
**When** I set up the development environment
**Then** requirements.txt contains all production dependencies (FastAPI, Pydantic v2, OpenAI SDK, etc.)
**And** requirements-dev.txt contains development dependencies (pytest, pytest-asyncio, ruff, mypy, etc.)
**And** docker-compose.yml is created with Redis service for rate limiting
**And** .env.example contains all required environment variables with documentation
**And** app/core/config.py exports a Settings object (Pydantic BaseSettings) that loads from environment
**And** I can run `pip install -r requirements-dev.txt` and install all dependencies
**And** I can run `docker-compose up` and start Redis locally

### Story 1.3: Containerize Application

As a developer,
I want a Docker container configuration for the application,
So that I can build and deploy the service consistently.

**Acceptance Criteria:**

**Given** the project structure and dependencies are set up
**When** I create the Docker configuration
**Then** Dockerfile uses multi-stage build with python:3.11-slim base image
**And** Dockerfile installs dependencies from requirements.txt
**And** Dockerfile exposes the FastAPI application port
**And** .dockerignore excludes unnecessary files (tests, docs, .git, etc.)
**And** I can run `docker build -t decisionflow .` and build the image successfully
**And** the built image is optimized for size and security

### Story 1.4: Set Up CI/CD Pipeline

As a developer,
I want a GitHub Actions CI/CD pipeline,
So that code changes are automatically tested and validated.

**Acceptance Criteria:**

**Given** the project structure is initialized
**When** I create the CI/CD pipeline
**Then** .github/workflows/ci.yml is created
**And** the pipeline runs on pull requests and pushes to main
**And** the pipeline installs dependencies and runs pytest test suite
**And** the pipeline runs linting checks (ruff or black)
**And** the pipeline runs type checking (mypy) if configured
**And** the pipeline builds the Docker image to verify Dockerfile correctness
**And** the pipeline fails if any checks fail

## Epic 2: Core Decision Analysis Pipeline

**Epic Goal:** API consumers can submit decision requests and receive structured, bias-aware, explainable recommendations through a deterministic multi-agent pipeline.

**User Outcome:** Users can POST decision requests to /v1/decisions/analyze and receive machine-readable JSON responses containing weighted criteria, trade-offs, explicit bias detections, confidence scores, and clear recommendations. The system processes requests through a fixed-order agent pipeline (Clarifier → Criteria Builder → Bias Checker → Option Evaluator → Decision Synthesizer) with schema validation at every step.

### Story 2.1: Implement Core Schemas and PipelineState

As a developer,
I want Pydantic models for all core data structures and PipelineState,
So that I have type-safe contracts for the entire pipeline.

**Acceptance Criteria:**

**Given** the project structure is initialized
**When** I implement core schemas
**Then** app/schemas/decision.py contains DecisionRequest and DecisionResponse models with all required fields
**And** app/schemas/state.py contains PipelineState model with request_id, versions, normalized input, agent outputs, and derived artifacts
**And** app/schemas/errors.py contains ErrorResponse model with error code, message, details, and request_id
**And** app/schemas/versioning.py contains version metadata models
**And** all Pydantic models have model_config = {"extra": "forbid"}
**And** all models use snake_case for field names
**And** unit tests exist for all schema models validating structure and constraints

### Story 2.2: Implement LLM Client Wrapper

As a developer,
I want an OpenAI SDK wrapper with retry logic and bounded concurrency,
So that agents can make LLM calls reliably.

**Acceptance Criteria:**

**Given** the project structure is initialized
**When** I implement the LLM client
**Then** app/llm/client.py provides a wrapper over OpenAI SDK with provider-agnostic interface
**And** app/llm/retry.py implements retry logic with max 2 retries, exponential backoff + jitter
**And** retry logic handles timeouts, transient 5xx errors, and network errors
**And** retry logic does NOT retry 4xx errors or business logic errors
**And** app/llm/prompts.py loads prompt templates from prompts/<logic_version>/ directory
**And** the client supports bounded concurrency with strict timeouts
**And** unit tests exist for retry logic and error handling
**And** unit tests mock OpenAI API calls

### Story 2.3: Implement Base Agent Interface

As a developer,
I want a base agent interface that all agents implement,
So that agents have consistent contracts and behavior.

**Acceptance Criteria:**

**Given** core schemas are implemented
**When** I implement the base agent interface
**Then** app/agents/base.py defines an abstract base class or protocol for agents
**And** the interface requires an async execute method that takes PipelineState and returns agent-specific output
**And** the interface enforces that all agents follow the same execution pattern
**And** unit tests exist for the base interface

### Story 2.4: Implement Clarifier Agent

As a developer,
I want the Clarifier Agent to identify missing inputs and ask essential questions,
So that the system can request necessary information before processing.

**Acceptance Criteria:**

**Given** the base agent interface and LLM client are implemented
**When** I implement the Clarifier Agent
**Then** app/agents/clarifier.py contains Clarifier class implementing the base agent interface
**And** app/schemas/agents.py contains ClarifierInput and ClarifierOutput Pydantic models
**And** the agent loads prompt from prompts/<logic_version>/clarifier.txt
**And** the agent identifies missing required inputs from the decision request
**And** the agent returns structured questions (not free-form text) in ClarifierOutput
**And** the agent output is validated against ClarifierOutput schema
**And** unit tests exist with mocked LLM responses
**And** unit tests verify the agent identifies missing inputs correctly

### Story 2.5: Implement Criteria Builder Agent

As a developer,
I want the Criteria Builder Agent to convert vague goals into weighted evaluation criteria,
So that options can be evaluated against structured criteria.

**Acceptance Criteria:**

**Given** the Clarifier Agent is implemented
**When** I implement the Criteria Builder Agent
**Then** app/agents/criteria_builder.py contains CriteriaBuilder class
**And** app/schemas/agents.py contains CriteriaBuilderInput and CriteriaBuilderOutput models
**And** CriteriaBuilderOutput contains criteria array with name, weight, and rationale for each criterion
**And** weights sum to 1.0 (normalized)
**And** the agent loads prompt from prompts/<logic_version>/criteria_builder.txt
**And** the agent output is validated against CriteriaBuilderOutput schema
**And** unit tests exist with mocked LLM responses
**And** unit tests verify criteria weights are normalized

### Story 2.6: Implement Bias Checker Agent

As a developer,
I want the Bias Checker Agent to detect and name specific cognitive biases,
So that bias findings can be separated from recommendations.

**Acceptance Criteria:**

**Given** the Criteria Builder Agent is implemented
**When** I implement the Bias Checker Agent
**Then** app/agents/bias_checker.py contains BiasChecker class
**And** app/schemas/agents.py contains BiasCheckerInput and BiasCheckerOutput models
**And** BiasCheckerOutput contains bias_findings array with bias_type (enum: sunk_cost, confirmation, optimism, authority), description, and evidence
**And** the agent detects all four bias types (sunk cost, confirmation, optimism, authority)
**And** the agent loads prompt from prompts/<logic_version>/bias_checker.txt
**And** the agent output is validated against BiasCheckerOutput schema
**And** unit tests exist with mocked LLM responses
**And** unit tests verify bias detection for each bias type

### Story 2.7: Implement Option Evaluator Agent

As a developer,
I want the Option Evaluator Agent to score each option against criteria with explicit justifications,
So that options can be compared objectively.

**Acceptance Criteria:**

**Given** the Bias Checker Agent is implemented
**When** I implement the Option Evaluator Agent
**Then** app/agents/option_evaluator.py contains OptionEvaluator class
**And** app/schemas/agents.py contains OptionEvaluatorInput and OptionEvaluatorOutput models
**And** OptionEvaluatorOutput contains scores per option per criterion with explicit justification
**And** scores are normalized (0.0 to 1.0 range)
**And** the agent loads prompt from prompts/<logic_version>/option_evaluator.txt
**And** the agent can score multiple options concurrently using asyncio.gather()
**And** the agent output is validated against OptionEvaluatorOutput schema
**And** unit tests exist with mocked LLM responses
**And** unit tests verify scoring and normalization

### Story 2.8: Implement Decision Synthesizer Agent

As a developer,
I want the Decision Synthesizer Agent to produce final recommendation with confidence score,
So that users receive a clear, defensible decision recommendation.

**Acceptance Criteria:**

**Given** the Option Evaluator Agent is implemented
**When** I implement the Decision Synthesizer Agent
**Then** app/agents/decision_synthesizer.py contains DecisionSynthesizer class
**And** app/schemas/agents.py contains DecisionSynthesizerInput and DecisionSynthesizerOutput models
**And** DecisionSynthesizerOutput contains winner, confidence score (0.0 to 1.0), trade-offs, assumptions, and what_would_change_the_decision
**And** confidence score is calculated based on input completeness, agent agreement, evidence strength, and detected biases
**And** the agent loads prompt from prompts/<logic_version>/decision_synthesizer.txt
**And** the agent output is validated against DecisionSynthesizerOutput schema
**And** unit tests exist with mocked LLM responses
**And** unit tests verify confidence score calculation

### Story 2.9: Implement Pipeline Orchestration

As a developer,
I want a pipeline orchestrator that executes agents in fixed order,
So that decision requests are processed deterministically.

**Acceptance Criteria:**

**Given** all five agents are implemented
**When** I implement pipeline orchestration
**Then** app/orchestration/pipeline.py contains the pipeline execution logic
**And** app/orchestration/runner.py contains the pipeline runner
**And** agents execute in fixed order: Clarifier → Criteria Builder → Bias Checker → Option Evaluator → Decision Synthesizer
**And** PipelineState is passed between agents (no direct agent-to-agent communication)
**And** each agent receives only the subset of PipelineState it needs
**And** each agent writes structured outputs to PipelineState
**And** the pipeline uses low temperature (or fixed) for LLM calls to ensure determinism
**And** unit tests exist for the complete pipeline execution
**And** integration tests verify the fixed execution order

### Story 2.10: Implement Schema Validation Service

As a developer,
I want a centralized schema validation service with repair capability,
So that all data is validated at three critical points.

**Acceptance Criteria:**

**Given** core schemas are implemented
**When** I implement the validation service
**Then** app/validation/service.py provides centralized validation utility
**And** validation occurs at three points: request payload, each agent step output, response payload
**And** app/validation/repair.py implements one-shot schema repair mechanism
**And** repair uses JSON Schema + validation errors to attempt fixing invalid outputs
**And** repair loads prompt from prompts/<logic_version>/repair.txt
**And** if repair fails, validation returns SCHEMA_VALIDATION_FAILED error
**And** app/validation/schemas.py contains JSON Schema definitions for repair
**And** unit tests exist for validation at all three points
**And** unit tests exist for repair mechanism (success and failure cases)

### Story 2.11: Implement Decision Analysis API Endpoint

As a developer,
I want the POST /v1/decisions/analyze endpoint,
So that API consumers can submit decision requests and receive recommendations.

**Acceptance Criteria:**

**Given** pipeline orchestration and validation are implemented
**When** I implement the API endpoint
**Then** app/api/v1/decisions.py contains the analyze_decision endpoint
**And** the endpoint accepts DecisionRequest and returns DecisionResponse
**And** the endpoint generates request_id (UUID v4) at entry point
**And** the endpoint validates request payload immediately on receipt
**And** the endpoint calls pipeline orchestration to process the request
**And** the endpoint validates response payload before returning
**And** the endpoint includes request_id in response
**And** the endpoint includes version metadata (api_version, logic_version, schema_version) in response meta field
**And** the endpoint handles errors and transforms to ErrorResponse format
**And** unit tests exist for successful request flow
**And** unit tests exist for validation error handling
**And** unit tests exist for pipeline error handling

### Story 2.12: Implement Error Handling and Standardized Error Responses

As a developer,
I want standardized error responses with request_id,
So that API consumers can debug issues and correlate errors.

**Acceptance Criteria:**

**Given** the API endpoint is implemented
**When** I implement error handling
**Then** app/core/exceptions.py contains typed exception classes (ValidationError, LLMError, AgentError, etc.)
**And** all errors are transformed to ErrorResponse format at API layer
**And** ErrorResponse contains error code, message, details, and request_id
**And** error codes are typed (SCHEMA_VALIDATION_FAILED, PROCESSING_ERROR, SYSTEM_ERROR, etc.)
**And** validation errors return 400 Bad Request
**And** processing errors return 500 Internal Server Error
**And** system errors (dependency unavailable) return 503 Service Unavailable
**And** all errors are logged with full context (request_id, agent, step) before transforming
**And** unit tests exist for all error scenarios

## Epic 3: Security & Access Control

**Epic Goal:** API consumers can securely authenticate and use the API with appropriate rate limiting and protection mechanisms.

**User Outcome:** Users authenticate using API keys (Bearer token or X-API-Key header), receive rate limit information in responses, and are protected from abuse through token-bucket rate limiting. Inputs are sanitized to prevent prompt injection attacks.

### Story 3.1: Implement API Key Authentication

As an API consumer,
I want to authenticate using API keys,
So that only authorized users can access the API.

**Acceptance Criteria:**

**Given** the API endpoint is implemented
**When** I implement API key authentication
**Then** app/api/middleware/auth.py validates API keys from Bearer token or X-API-Key header
**And** API keys are loaded from environment variable allowlist (MVP)
**And** app/core/config.py Settings object contains api_keys list
**And** invalid or missing API keys return 401 Unauthorized with ErrorResponse
**And** authentication middleware runs before route handlers
**And** FastAPI dependency injection is used for auth (app/api/dependencies.py)
**And** unit tests exist for valid API key authentication
**And** unit tests exist for invalid/missing API key rejection

### Story 3.2: Implement Rate Limiting with Redis

As an API consumer,
I want rate limiting per API key with token bucket algorithm,
So that API usage is controlled and protected from abuse.

**Acceptance Criteria:**

**Given** API key authentication is implemented
**When** I implement rate limiting
**Then** app/api/middleware/rate_limit.py implements token-bucket rate limiting
**And** rate limiting uses Redis for distributed rate limit tracking
**And** rate limit is 60 requests per minute per API key
**And** burst allowance is 20 requests
**And** rate limit exceeded returns 429 Too Many Requests with ErrorResponse
**And** response headers include X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
**And** response includes Retry-After header when rate limit exceeded
**And** rate limiting middleware runs after authentication, before route handlers
**And** unit tests exist with mocked Redis
**And** unit tests verify token bucket algorithm behavior
**And** unit tests verify rate limit headers

### Story 3.3: Implement Input Sanitization

As a developer,
I want input sanitization at the API layer,
So that prompt injection attacks are prevented.

**Acceptance Criteria:**

**Given** the API endpoint is implemented
**When** I implement input sanitization
**Then** app/core/sanitization.py provides input sanitization functions
**And** sanitization includes normalization, strict schema validation, size limits, and redaction
**And** payload size limit is enforced (max 256KB request size)
**And** option and criteria count limits are enforced to bound processing costs
**And** sanitization occurs at API layer before pipeline execution
**And** only validated, sanitized data is passed to agents (structured subsets)
**And** size limit exceeded returns 400 Bad Request with clear error message
**And** unit tests exist for all sanitization checks
**And** unit tests verify prompt injection attempts are blocked

## Epic 4: Observability & Operations

**Epic Goal:** Operators can monitor system health, check versions, debug issues, and understand system behavior through structured logging and metrics.

**User Outcome:** Operators can check service liveness (/health), verify readiness (/ready), retrieve version metadata (/v1/meta), and correlate logs and metrics using request_id. System provides structured logging with request_id correlation and basic metrics (latency P50/P95, error rate, schema failure rate).

### Story 4.1: Implement Health and Readiness Endpoints

As an operator,
I want health and readiness endpoints,
So that I can monitor service availability and dependency status.

**Acceptance Criteria:**

**Given** the API structure is set up
**When** I implement health endpoints
**Then** app/api/health.py contains GET /health endpoint for liveness checks
**And** app/api/ready.py contains GET /ready endpoint for readiness checks
**And** /health returns 200 OK when service is running
**And** /ready returns 200 OK when model/tool dependencies are available
**And** /ready returns 503 Service Unavailable when dependencies are unavailable
**And** endpoints do not require authentication (operational endpoints)
**And** unit tests exist for both endpoints

### Story 4.2: Implement Version Metadata Endpoint

As an API consumer,
I want to retrieve service version information,
So that I can check version compatibility and track changes.

**Acceptance Criteria:**

**Given** the API structure is set up
**When** I implement version metadata endpoint
**Then** app/api/v1/meta.py contains GET /v1/meta endpoint
**And** the endpoint returns service version, logic version, schema version, and build hash
**And** logic version is read from prompts/<logic_version>/ directory
**And** schema version is tracked in PipelineState and Pydantic models
**And** API version is from URL path (/v1/...)
**And** the endpoint does not require authentication (metadata endpoint)
**And** unit tests exist for the endpoint

### Story 4.3: Implement Structured Logging

As an operator,
I want structured logging with request_id correlation,
So that I can debug issues and trace request flows.

**Acceptance Criteria:**

**Given** the application structure is set up
**When** I implement structured logging
**Then** app/core/logging.py sets up structured logging (JSON format for production, key-value for development)
**And** all log entries include request_id when available
**And** log levels are used correctly (DEBUG, INFO, WARNING, ERROR, CRITICAL)
**And** structured fields are included: level, request_id, agent, duration_ms, status, etc.
**And** NO raw user input or LLM prompts/responses are logged (security/privacy)
**And** agent step outputs (structured data) are logged, not raw LLM responses
**And** logging is configured at application startup
**And** unit tests verify logging format and content

### Story 4.4: Implement Metrics Collection

As an operator,
I want basic metrics for system monitoring,
So that I can track performance and identify issues.

**Acceptance Criteria:**

**Given** structured logging is implemented
**When** I implement metrics collection
**Then** app/metrics/collection.py provides metrics collection functions
**And** metrics include latency (P50, P95), error rate, and schema failure rate
**And** app/metrics/middleware.py provides metrics middleware for FastAPI
**And** metrics are collected per endpoint and per agent
**And** metrics include request_id correlation
**And** Prometheus-style metrics format is used
**And** unit tests exist for metrics collection

## Epic 5: Quality Assurance & Testing

**Epic Goal:** Developers and operators can validate system correctness, perform regression testing, and access comprehensive documentation for integration.

**User Outcome:** Developers can run golden decision test suite for regression testing, compare outputs across logic versions, and validate prompt changes. API consumers can access OpenAPI 3.0 specification, code samples, integration guides, and error handling examples.

### Story 5.1: Implement Evaluation Harness

As a developer,
I want an evaluation harness for regression testing,
So that I can validate system correctness across prompt versions.

**Acceptance Criteria:**

**Given** the pipeline and agents are implemented
**When** I implement the evaluation harness
**Then** app/evaluation/harness.py provides evaluation harness functionality
**And** app/evaluation/comparison.py provides output comparison across versions
**And** app/evaluation/golden.py provides golden decision test utilities
**And** golden decisions are stored in tests/golden/ with folder-per-case structure
**And** each golden case has input.json, expected_output.json, and metadata.yaml
**And** comparison uses structured comparison (not semantic similarity)
**And** hard gates include schema validity, determinism, and invariant assertions
**And** unit tests exist for the evaluation harness

### Story 5.2: Create Golden Decision Test Suite

As a developer,
I want a golden decision test suite,
So that I can perform regression testing on decision logic.

**Acceptance Criteria:**

**Given** the evaluation harness is implemented
**When** I create golden decision tests
**Then** tests/golden/ contains at least 2-3 golden decision cases
**And** each case folder contains input.json, expected_output.json, and metadata.yaml
**And** test cases cover different decision types (build vs. buy, vendor selection, etc.)
**And** pytest tests can load and run golden decision cases
**And** tests verify schema validity, determinism, and invariant assertions
**And** tests/golden/README.md documents the golden decision structure

### Story 5.3: Integrate Evaluation Harness into CI/CD

As a developer,
I want the evaluation harness integrated into CI/CD,
So that regression tests run automatically on code changes.

**Acceptance Criteria:**

**Given** the evaluation harness and golden tests are implemented
**When** I integrate into CI/CD
**Then** .github/workflows/ci.yml runs a small subset of golden tests on pull requests
**And** .github/workflows/ci.yml runs the full golden test suite nightly
**And** CI fails if regression tests fail (schema breaks, determinism breaks, invariant failures)
**And** CI reports repair-rate spikes as warnings
**And** the CI pipeline is documented

### Story 5.4: Generate OpenAPI Documentation

As an API consumer,
I want OpenAPI 3.0 specification for all endpoints,
So that I can integrate with the API using standard tools.

**Acceptance Criteria:**

**Given** all API endpoints are implemented
**When** I generate OpenAPI documentation
**Then** FastAPI automatically generates OpenAPI 3.0 specification
**And** docs/api/openapi.json contains the generated specification
**And** scripts/generate_openapi.py can regenerate the specification
**And** the specification includes all endpoints with request/response schemas
**And** the specification includes error response schemas
**And** the specification is accessible via /docs and /redoc endpoints (FastAPI default)

### Story 5.5: Create Integration Documentation

As an API consumer,
I want integration guides and code samples,
So that I can quickly integrate with the API.

**Acceptance Criteria:**

**Given** the API is implemented and OpenAPI spec is generated
**When** I create integration documentation
**Then** docs/ contains integration guides
**And** documentation includes code samples in cURL, Python, and Node.js
**And** documentation includes error handling examples
**And** documentation includes troubleshooting guides
**And** documentation follows the architecture and project context patterns

