"""Version metadata models."""

from pydantic import BaseModel, Field


class VersionMetadata(BaseModel):
    """Version information for API responses."""

    api_version: str = Field(..., description="API contract version (e.g., 'v1')")
    logic_version: str = Field(
        ..., description="Prompt bundle / agent pipeline version (e.g., '1.2.3')"
    )
    schema_version: str = Field(
        ..., description="JSON schema version (e.g., '1.0.0')"
    )

    model_config = {"extra": "forbid"}


