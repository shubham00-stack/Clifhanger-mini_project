"""Phase 7 Security tests: Filename sanitization, payload limits, and tenancy boundaries."""

import pytest
from uuid import uuid4
from packages.shared.security import sanitize_filename, validate_payload_size, enforce_project_tenancy
from packages.shared.errors import TenancyError, ValidationError


def test_sanitize_filename_prevents_directory_traversal():
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe") == "cmd.exe"
    assert sanitize_filename("script; rm -rf /") == "script__rm_-rf_"
    assert sanitize_filename("") == "untitled_asset.txt"


def test_validate_payload_size_enforcement():
    small_data = b"Hello World" * 10
    # Should not raise
    validate_payload_size(small_data, max_allowed_bytes=1000)

    large_data = b"X" * 1500
    with pytest.raises(ValidationError):
        validate_payload_size(large_data, max_allowed_bytes=1000)


def test_enforce_project_tenancy_boundary():
    proj_a = uuid4()
    proj_b = uuid4()

    # Same project passes
    enforce_project_tenancy(proj_a, proj_a)

    # Different project raises TenancyError
    with pytest.raises(TenancyError):
        enforce_project_tenancy(proj_a, proj_b)
