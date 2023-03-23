"""matcha custom errors."""
from typing import Any


class MatchaPermissionError(Exception):
    """Matcha Permission Error.

    Raised when there are not enough permissions on a directory.
    """

    def __init__(self, path: str, *args: Any, **kwargs: Any):
        """Initialise Matcha Permission Error.

        Args:
            path: path that the user does not have permission for
            *args: args
            **kwargs: kwargs
        """
        message = f"We do not have permission to write the configuration. Check if you have write permissions for '{path}'."
        super().__init__(message, *args, **kwargs)
