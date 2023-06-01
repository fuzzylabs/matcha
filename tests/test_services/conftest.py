"""Configuration tests for the test_services module."""
import random
import uuid

import pytest


@pytest.fixture(scope="module", autouse=True)
def random_state():
    """A fixture to ensure the random state is fixed for the tests."""
    random.seed(42)


@pytest.fixture
def uuid_for_testing() -> uuid.UUID:
    """A random UUID4 that can be used as a fixture in the tests.

    Returns:
        uuid.UUID: a UUID4 which remains the same across tests.
    """
    return uuid.UUID(int=random.getrandbits(128), version=4)
