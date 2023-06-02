"""Tests for services._validation."""
from uuid import UUID

import pytest

from matcha_ml.errors import MatchaError
from matcha_ml.services._validation import _check_uuid


def test_valid_uuid(uuid_for_testing: UUID):
    """Test that when a valid uuid is passed, the check passes.

    Args:
        uuid_for_testing (UUID): a UUID created for testing purposes.
    """
    assert _check_uuid(str(uuid_for_testing))


def test_invalid_uuid():
    """Test that when an invalid UUID is passed, the check fails and an exception is raised."""
    with pytest.raises(MatchaError):
        _check_uuid("this-is-not-a-uuid")
