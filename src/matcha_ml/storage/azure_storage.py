"""Class to interact with Azure Storage."""


class AzureStorage:
    """Class to interact with Azure blob storage."""

    account_name: str

    def __init__(self, account_name: str) -> None:
        """Initialize Azure Storage.

        Args:
            account_name: Azure storage account name
        """
        ...

    def container_exists(self, container_name: str) -> bool:
        """Check if storage container exists.

        Args:
            container_name: Azure storage container name
        Returns:
            bool: does container exist.
        """
        return False
