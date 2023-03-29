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


class MatchaAuthenticationError(Exception):
    """Matcha Authentication Error.

    Raised when the user is not authenticated with an external service.
    """

    def __init__(self, service_name: str, *args: Any, **kwargs: Any):
        """Initialise Matcha Authentication Error.

        Args:
            service_name (str): Service in which the user is not authenticated
            *args: args
            **kwargs: kwargs
        """
        message = f"Error, Matcha couldn't authenticate you with {service_name}!"
        if service_name == "Azure":
            message += (
                " Make sure to run 'az login' before trying to provision resources."
            )
        super().__init__(message, *args, **kwargs)
