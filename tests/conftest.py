"""Reusable fixtures."""
import json
import os
import random
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Iterator
from unittest.mock import PropertyMock, patch

import pytest
from azure.mgmt.confluent.models._confluent_management_client_enums import (
    ProvisionState,  # type: ignore [import]
)
from typer.testing import CliRunner

from matcha_ml.config import (
    MatchaConfig,
    MatchaConfigComponent,
    MatchaConfigComponentProperty,
    MatchaConfigService,
)
from matcha_ml.services import AzureClient
from matcha_ml.services.azure_service import ROLE_ID_MAPPING
from matcha_ml.services.terraform_service import TerraformConfig
from matcha_ml.state.matcha_state import (
    MATCHA_STATE_PATH,
    MatchaResource,
    MatchaResourceProperty,
    MatchaState,
    MatchaStateComponent,
)

UUID_VERSION = 4
INTERNAL_FUNCTION_STUB = "matcha_ml.services.AzureClient"


@pytest.fixture
def runner() -> CliRunner:
    """A fixture for cli runner."""
    return CliRunner()


@pytest.fixture
def matcha_testing_directory() -> Iterator[str]:
    """A fixture for creating and removing temporary test directory for storing and moving files.

    Yields:
        str: a path to temporary directory for storing and moving files from tests.
    """
    temp_dir = tempfile.TemporaryDirectory()
    original_working_directory = (
        os.getcwd()
    )  # save in case a test changes to temp directory which will be deleted

    # tests are executed at this point
    yield temp_dir.name

    # delete temp folder
    os.chdir(original_working_directory)  # restore original working directory
    temp_dir.cleanup()


@pytest.fixture(autouse=True)
def mocked_azure_client() -> AzureClient:
    """The Azure Client with mocked variables.

    Returns:
        AzureClient: the mocked AzureClient.
    """
    with patch(f"{INTERNAL_FUNCTION_STUB}._check_authentication") as auth, patch(
        f"{INTERNAL_FUNCTION_STUB}._subscription_id"
    ) as sub, patch(f"{INTERNAL_FUNCTION_STUB}.fetch_resource_groups") as rg, patch(
        f"{INTERNAL_FUNCTION_STUB}.resource_group_state"
    ) as rg_state, patch(
        f"{INTERNAL_FUNCTION_STUB}._fetch_user_roles"
    ) as roles, patch(
        f"{INTERNAL_FUNCTION_STUB}.fetch_storage_access_key"
    ) as key, patch(
        f"{INTERNAL_FUNCTION_STUB}.fetch_regions"
    ) as valid_regions, patch(
        f"{INTERNAL_FUNCTION_STUB}.fetch_resource_group_names"
    ) as current_rg_names:
        auth.return_value = True
        sub.return_value = "id"
        rg.return_value = None
        rg_state.return_value = ProvisionState.SUCCEEDED
        roles.return_value = [
            f"/subscriptions/id/providers/Microsoft.Authorization/roleDefinitions/{ROLE_ID_MAPPING['Owner']}",
            f"/subscriptions/id/providers/Microsoft.Authorization/roleDefinitions/{ROLE_ID_MAPPING['Contributor']}",
        ]
        key.return_value = "key"
        valid_regions.return_value = {"ukwest", "uksouth"}
        current_rg_names.return_value = {"rand-resources"}

        yield AzureClient()


@pytest.fixture(autouse=True)
def mocked_segment_track_decorator():
    """Mock for Segment track.

    Yields:
        MagicMock: Mocked segment track function.
    """
    with patch(
        "matcha_ml.services.analytics_service.analytics.Client.track"
    ) as track_analytics:
        track_analytics.return_value = (True, "test_message")

        yield track_analytics


@pytest.fixture(autouse=True)
def random_state():
    """A fixture to ensure the random state is fixed for the tests."""
    random.seed(42)


@pytest.fixture
def uuid_for_testing() -> uuid.UUID:
    """A random UUID4 that can be used as a fixture in the tests.

    Returns:
        uuid.UUID: a UUID4 which remains the same across tests.
    """
    return uuid.UUID(int=random.getrandbits(128), version=UUID_VERSION)


@pytest.fixture(autouse=True)
def mock_uuid(uuid_for_testing) -> None:
    """Mock the return value for UUID4 function.

    Args:
        uuid_for_testing (uuid.UUID): a fixed valid UUID4 value.
    """
    with patch("matcha_ml.state.matcha_state.uuid.uuid4") as uuid_mock:
        uuid_mock.return_value = uuid_for_testing
        yield


@pytest.fixture(autouse=True)
def mocked_terraform_config(matcha_testing_directory) -> TerraformConfig:
    """Mock for the TerraformConfig working directory.

    Returns:
        TerraformConfig: the mocked TerraformConfig.
    """
    with patch(
        "matcha_ml.services.terraform_service.TerraformConfig.working_dir",
        new_callable=PropertyMock,
    ) as working_dir:
        working_dir.return_value = str(matcha_testing_directory)

        yield TerraformConfig()


@pytest.fixture()
def mock_state_file(matcha_testing_directory: str, uuid_for_testing: uuid.UUID) -> Path:
    """A fixture for mocking a test state file in the test directory.

    Args:
        matcha_testing_directory (str): the test directory
        uuid_for_testing (uuid.UUID): a UUID4 which remains the same across tests.

    Returns:
        Path: Path object to matcha.state file
    """
    os.chdir(matcha_testing_directory)

    matcha_infrastructure_dir = os.path.join(".matcha", "infrastructure", "resources")
    os.makedirs(matcha_infrastructure_dir)

    state_file_resources = {
        "cloud": {"flavor": "azure", "resource-group-name": "test_resources"},
        "container-registry": {
            "flavor": "azure",
            "registry-name": "azure_registry_name",
            "registry-url": "azure_container_registry",
        },
        "pipeline": {
            "flavor": "zenml",
            "connection-string": "zenml_test_connection_string",
            "server-password": "zen_server_password",
            "server-url": "zen_server_url",
        },
        "experiment-tracker": {"flavor": "mlflow", "tracking-url": "mlflow_test_url"},
        "id": {"matcha_uuid": str(uuid_for_testing)},
    }

    with open(MATCHA_STATE_PATH, "w") as f:
        json.dump(state_file_resources, f)

    return Path(MATCHA_STATE_PATH)


@pytest.fixture
def state_file_as_object(uuid_for_testing: uuid.UUID) -> MatchaState:
    """A fixture to represent the Matcha state as a MatchaState object.

    Args:
        uuid_for_testing (uuid.UUID): Fixed valid UUID for testing.

    Returns:
        MatchaState: the Matcha state testing fixture.
    """
    return MatchaState(
        components=[
            MatchaStateComponent(
                resource=MatchaResource("cloud"),
                properties=[
                    MatchaResourceProperty("flavor", "azure"),
                    MatchaResourceProperty("resource-group-name", "test_resources"),
                ],
            ),
            MatchaStateComponent(
                resource=MatchaResource("container-registry"),
                properties=[
                    MatchaResourceProperty("flavor", "azure"),
                    MatchaResourceProperty("registry-name", "azure_registry_name"),
                    MatchaResourceProperty("registry-url", "azure_container_registry"),
                ],
            ),
            MatchaStateComponent(
                resource=MatchaResource("pipeline"),
                properties=[
                    MatchaResourceProperty("flavor", "zenml"),
                    MatchaResourceProperty(
                        "connection-string", "zenml_test_connection_string"
                    ),
                    MatchaResourceProperty("server-password", "zen_server_password"),
                    MatchaResourceProperty("server-url", "zen_server_url"),
                ],
            ),
            MatchaStateComponent(
                resource=MatchaResource("experiment-tracker"),
                properties=[
                    MatchaResourceProperty("flavor", "mlflow"),
                    MatchaResourceProperty("tracking-url", "mlflow_test_url"),
                ],
            ),
            MatchaStateComponent(
                resource=MatchaResource("id"),
                properties=[
                    MatchaResourceProperty("matcha_uuid", str(uuid_for_testing)),
                ],
            ),
        ]
    )


@pytest.fixture
def mocked_matcha_config_json_object() -> Dict[str, Dict[str, str]]:
    """A fixture returning a dictionary representation of the matcha.config.json file.

    Returns:
        matcha_config (Dict[str, Dict[str, str]]): a dictionary representation of the matcha.config.json file
    """
    matcha_config = {
        "remote_state_bucket": {
            "account_name": "test-account",
            "container_name": "test-container",
            "resource_group_name": "test-rg",
        }
    }

    return matcha_config


@pytest.fixture
def mocked_matcha_config_component_property() -> MatchaConfigComponentProperty:
    """A fixture returning a mocked MatchaConfigComponentProperty instance.

    Returns:
        (MatchaConfigComponentProperty): a mocked MatchaConfigComponentProperty instance.
    """
    return MatchaConfigComponentProperty(name="account_name", value="test_account_name")


@pytest.fixture
def mocked_matcha_config_component(mocked_matcha_config_json_object):
    """A fixture returning a mocked MatchaConfigComponentProperty instance.

    Args:
        mocked_matcha_config_json_object (Dict[str, Dict[str, str]]): a dictionary representation of the matcha.config.json file

    Returns:
        (MatchaConfigComponentProperty): a mocked MatchaConfigComponentProperty instance.
    """
    properties = []
    for key, value in mocked_matcha_config_json_object["remote_state_bucket"].items():
        properties.append(MatchaConfigComponentProperty(name=key, value=value))

    return MatchaConfigComponent(name="remote_state_bucket", properties=properties)


@pytest.fixture
def mocked_matcha_config(mocked_matcha_config_component):
    """A fixture returning a mocked MatchaConfig instance.

    Args:
        mocked_matcha_config_component (MatchaConfigComponent): a mocked MatchaConfigComponent instance.

    Returns:
        (MatchaConfig): a mocked MatchaConfig instance.
    """
    return MatchaConfig([mocked_matcha_config_component])


@pytest.fixture
def mocked_matcha_config_service():
    """A fixture representing a mocked MatchaConfigService.

    Returns:
    (MatchaConfigService): a mocked MatchaConfigService instance.
    """
    return MatchaConfigService()


@pytest.fixture
def mocked_remote_state_manager_is_state_provisioned_false():
    """A fixture for providing context within which RemoteStateManager.is_state_provisioned always returns false.

    Yields:
        A mocked RemoteStateManager object with a patched is_state_provisioned method.
    """
    with patch(
        "matcha_ml.state.remote_state_manager.RemoteStateManager.is_state_provisioned"
    ) as is_state_provisioned:
        is_state_provisioned.return_value = False
        yield is_state_provisioned
