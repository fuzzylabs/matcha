"""matcha custom errors."""
from typing import Any


class MatchaError(Exception):
    """Matcha generic Error."""

    def __init__(self, message: str, *args: Any, **kwargs: Any):
        """Initialise Matcha Error.

        Args:
            message: the error message to propagate to the user
            *args: args
            **kwargs: kwargs
        """
        super().__init__(message, *args, **kwargs)


class MatchaPermissionError(MatchaError):
    """Matcha Permission Error.

    Raised when the user does not have the appropriate permissions.
    """

    def __init__(self, message: str, *args: Any, **kwargs: Any):
        """Initialise Matcha Permission Error.

        Args:
            message: the error message to propagate to the user
            *args: args
            **kwargs: kwargs
        """
        super().__init__(message, *args, **kwargs)


class MatchaAuthenticationError(MatchaError):
    """Matcha Authentication Error.

    Raised when the user is not authenticated with an external service.
    """

    def __init__(self, auth_error: str, *args: Any, **kwargs: Any):
        """The initialiser for the Authentication error.

        Args:
            auth_error (str): the error to propagate to the user.
            *args: additional arguments to pass to the Exception base class.
            **kwargs: additional key word arguments to pass to the Exception base class.
        """
        message = f"Error - Matcha couldn't authenticate you with Azure: {auth_error}, make sure you've run 'az login'!"
        super().__init__(message, *args, **kwargs)


class MatchaInputError(MatchaError):
    """Matcha Input Error.

    Raised when the user inputs a bad value.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        """The initialiser for Input error.

        Args:
            *args: additional arguments to pass to the Exception base class.
            **kwargs: additional key word arguments to pass to the Exception base class.
        """
        super().__init__(*args, **kwargs)


class MatchaTerraformError(MatchaError):
    """Matcha Terraform Error.

    Raised when terraform fails to run.
    """

    def __init__(self, tf_error: str, *args: Any, **kwargs: Any):
        """Initialise Matcha Terraform Error.

        Args:
            tf_error: terraform error
            *args: args
            **kwargs: kwargs
        """
        message = f"Terraform failed because of the following error: '{tf_error}'."
        super().__init__(message, *args, **kwargs)
