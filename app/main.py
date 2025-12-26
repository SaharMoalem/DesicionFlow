"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError as PydanticValidationError

from app.api import health, ready
from app.api.middleware.error_handlers import (
    agent_error_handler,
    decision_flow_error_handler,
    generic_exception_handler,
    llm_error_handler,
    validation_error_handler,
    validation_exception_handler,
)
from app.api.middleware.request_id import RequestIDMiddleware
from app.api.v1 import decisions
from app.core.config import settings
from app.core.logging import setup_logging

# Setup logging
setup_logging()
from app.core.exceptions import (
    AgentError,
    DecisionFlowError,
    LLMError,
    ValidationError,
)

# Create FastAPI application
app = FastAPI(
    title="DecisionFlow",
    description="Multi-Agent Decision & Trade-off Analyzer",
    version=settings.logic_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware (allow all origins in development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development() else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Register global exception handlers
app.add_exception_handler(PydanticValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(AgentError, agent_error_handler)
app.add_exception_handler(LLMError, llm_error_handler)
app.add_exception_handler(DecisionFlowError, decision_flow_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Register operational endpoints (no authentication required)
app.include_router(health.router, tags=["operational"])
app.include_router(ready.router, tags=["operational"])

# Register API v1 endpoints
app.include_router(decisions.router)

# Serve static files for frontend (development only)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Check if frontend directory exists
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        """Serve frontend index page."""
        return FileResponse(os.path.join(frontend_path, "index.html"))
    
    # Serve CSS and JS files directly
    @app.get("/styles.css", include_in_schema=False)
    async def serve_css():
        return FileResponse(os.path.join(frontend_path, "styles.css"), media_type="text/css")
    
    @app.get("/app.js", include_in_schema=False)
    async def serve_js():
        return FileResponse(os.path.join(frontend_path, "app.js"), media_type="application/javascript")
else:
    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {
            "service": "DecisionFlow",
            "version": settings.logic_version,
            "status": "running",
            "docs": "/docs",
        }

