"""Settings/configuration (Pydantic BaseSettings)."""

from enum import Enum
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Environment types."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Log formats."""

    JSON = "json"
    TEXT = "text"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
    )

    # API Configuration
    api_version: str = Field(default="v1", description="API version (used in URL paths)")
    logic_version: str = Field(
        default="v1.0.0", description="Logic version (prompt bundle version)"
    )
    schema_version: str = Field(
        default="v1.0.0", description="Schema version (for compatibility tracking)"
    )

    # API Authentication
    allowed_api_keys: str = Field(
        default="",
        description="Comma-separated list of allowed API keys",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key (required)",
    )
    openai_model: str = Field(
        default="gpt-3.5-turbo",
        description="OpenAI model to use (e.g., 'gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo-preview')",
    )
    openai_max_tokens: int = Field(
        default=2000,
        ge=1,
        le=8000,
        description="Maximum tokens for LLM responses",
    )
    openai_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM calls (0.0 for deterministic output)",
    )

    # LLM Configuration
    llm_max_concurrent_requests: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum concurrent LLM requests",
    )
    llm_request_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout in seconds",
    )

    # Redis Configuration
    redis_host: str = Field(
        default="localhost",
        description="Redis host",
    )
    redis_port: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="Redis port",
    )
    redis_db: int = Field(
        default=0,
        ge=0,
        le=15,
        description="Redis database number",
    )
    redis_password: str = Field(
        default="",
        description="Redis password (leave empty for local development)",
    )
    redis_pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Redis connection pool size",
    )

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(
        default=60,
        ge=1,
        description="Requests per minute per API key",
    )
    rate_limit_burst: int = Field(
        default=20,
        ge=1,
        description="Burst capacity",
    )

    # Logging
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Log level",
    )
    log_format: LogFormat = Field(
        default=LogFormat.JSON,
        description="Log format (json or text)",
    )

    # Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Environment (development, staging, production)",
    )

    # Application Configuration
    app_host: str = Field(
        default="0.0.0.0",
        description="Application host",
    )
    app_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Application port",
    )
    app_reload: bool = Field(
        default=True,
        description="Enable auto-reload in development",
    )

    def get_allowed_api_keys(self) -> List[str]:
        """Parse comma-separated API keys into a list."""
        if not self.allowed_api_keys:
            return []
        return [key.strip() for key in self.allowed_api_keys.split(",") if key.strip()]

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION


# Global settings instance
settings = Settings()

