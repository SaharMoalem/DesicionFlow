"""Tests for versioning schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.versioning import VersionMetadata


def test_version_metadata_valid() -> None:
    """Test VersionMetadata with valid data."""
    meta = VersionMetadata(
        api_version="v1",
        logic_version="1.0.0",
        schema_version="1.0.0",
    )
    assert meta.api_version == "v1"
    assert meta.logic_version == "1.0.0"
    assert meta.schema_version == "1.0.0"


def test_version_metadata_extra_fields_forbidden() -> None:
    """Test VersionMetadata rejects extra fields."""
    with pytest.raises(ValidationError) as exc_info:
        VersionMetadata(
            api_version="v1",
            logic_version="1.0.0",
            schema_version="1.0.0",
            extra_field="not allowed",
        )
    assert "extra" in str(exc_info.value).lower() and "not permitted" in str(
        exc_info.value
    ).lower()


def test_version_metadata_required_fields() -> None:
    """Test VersionMetadata requires all fields."""
    with pytest.raises(ValidationError):
        VersionMetadata(
            api_version="v1",
            # Missing logic_version and schema_version
        )

