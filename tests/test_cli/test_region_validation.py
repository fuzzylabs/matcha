"""Test suite to test the region validation."""
import click
import pytest
from azure.identity import AzureCliCredential
from azure.mgmt.resource import SubscriptionClient

from matcha_ml.cli.region_validation import verify_azure_location


@pytest.mark.parametrize(
    "location_name, expectation",
    [
        ("ukweest", click.exceptions.BadParameter),  # Mispelled location
        ("mordorwest", click.exceptions.BadParameter),  # Invalid location
    ],
)
def test_verify_azure_location(
    location_name: str,
    expectation: Exception,
    monkeypatch,
):
    """Test that Azure location is being correctly verified.

    Args:
        location_name (str): Input location name
        expectation (Exception): expected exception
        monkeypatch (pytest.monkeypatch.MonkeyPatch): Pytest monkeypatch for patching a function
    """

    def mock_get_azure_locations(subscription_client: SubscriptionClient) -> list:
        """Mock function for getting a list of Azure locations.

        Returns:
            list: Mock list of locations
        """
        return ["ukwest", "uksouth"]

    def mock_get_azure_subscription_client() -> SubscriptionClient:
        """Mock function for checking Azure authentication.

        Returns:
            SubscriptionClient: Mock Azure subscription client
        """
        return SubscriptionClient(AzureCliCredential())

    def mock_check_azure_is_authenticated() -> None:
        """Mock function for checking Azure authentication."""
        return None

    monkeypatch.setattr(
        "matcha_ml.cli.region_validation.get_azure_locations",
        mock_get_azure_locations,
    )

    monkeypatch.setattr(
        "matcha_ml.cli.region_validation.get_azure_subscription_client",
        mock_get_azure_subscription_client,
    )

    monkeypatch.setattr(
        "matcha_ml.cli.region_validation.check_azure_is_authenticated",
        mock_check_azure_is_authenticated,
    )

    with pytest.raises(expectation):
        verify_azure_location(location_name)
