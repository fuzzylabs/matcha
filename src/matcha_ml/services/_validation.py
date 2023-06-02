"""Common validation functions for the services."""

from uuid import UUID

from matcha_ml.errors import MatchaError

UUID_VERSION = 4


def _check_uuid(uuid: str) -> bool:
    """Checks whether a string is a valid UUID.

    Args:
        uuid (str): the possible UUID to check.

    Raises:
        MatchaError: if the uuid parameter cannot be parsed as a UUID object.

    Returns:
        bool: True when the UUID is valid.
    """
    try:
        str(UUID(uuid, version=UUID_VERSION))
    except ValueError:
        raise MatchaError(
            "Error - the user or environment unique identifier is malformed."
        )

    return True
