"""Security utilities: safe filename sanitization, payload limits, tenancy boundaries."""

import os
import re
from typing import Any
from uuid import UUID
from .errors import TenancyError, ValidationError


_SAFE_FILENAME_REGEX = re.compile(r"[^a-zA-Z0-9_\-\.]")


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes filenames to prevent path traversal and arbitrary command injection.
    Strips directory separators, handles Windows/Unix path tricks, and restricts to safe characters.
    """
    if not filename or not filename.strip():
        return "untitled_asset.txt"

    # Normalize slashes and strip trailing slashes
    clean_path = filename.replace("\\", "/").strip().rstrip("/")
    # Take only the base name (strip any leading path components)
    clean = os.path.basename(clean_path)
    # Replace non-whitelisted characters with underscore
    clean = _SAFE_FILENAME_REGEX.sub("_", clean)
    # Avoid hidden dotfiles or empty extensions
    clean = clean.lstrip(".")
    if not clean:
        clean = "sanitized_asset.txt"
    # Bound max filename length
    return clean[:200]


def validate_payload_size(data_bytes: bytes, max_allowed_bytes: int = 10485760) -> None:
    """Verifies payload does not exceed the allowed size limit (default 10MB)."""
    if len(data_bytes) > max_allowed_bytes:
        raise ValidationError(
            f"Payload size ({len(data_bytes)} bytes) exceeds maximum limit ({max_allowed_bytes} bytes)."
        )


def enforce_project_tenancy(entity_project_id: UUID, expected_project_id: UUID) -> None:
    """Verifies that an entity strictly belongs to the authenticated project boundary."""
    if entity_project_id != expected_project_id:
        raise TenancyError(
            f"Cross-project access violation: expected project {expected_project_id}, found {entity_project_id}"
        )
