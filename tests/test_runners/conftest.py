"""Reusable fixtures."""
import os
from typing import Tuple

import pytest


@pytest.fixture
def mock_matcha_template_folder(matcha_testing_directory: str) -> Tuple[str, str]:
    """Fixture that sets up a mock .matcha directory structure for testing purposes.

    Two files are also populated to this test directory, one in root and one inside the sub folder.

    Args:
        matcha_testing_directory (str): temporary working directory for tests.
    """
    os.chdir(matcha_testing_directory)

    mock_template_folder_path = os.path.join(matcha_testing_directory, ".matcha")
    os.mkdir(mock_template_folder_path)

    mock_sub_folder_path = os.path.join(mock_template_folder_path, "sub_folder")
    os.mkdir(mock_sub_folder_path)

    # Populate some files
    root_file = os.path.join(mock_template_folder_path, "root_file")
    sub_file = os.path.join(mock_sub_folder_path, "sub_file")

    # Create a mock file in `.matcha/`
    with open(root_file, "a"):
        ...
    # Create a mock file in `.matcha/sub_folder/`
    with open(sub_file, "a"):
        ...

    yield matcha_testing_directory, mock_template_folder_path

    # There is no logic to remove the directory on purpose as this is for testing clean_up() which will remove the testing .matcha directory.
