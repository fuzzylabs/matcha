"""Reusable fixtures."""
import os
import shutil
from typing import Tuple

import pytest


@pytest.fixture
def mock_infrastructure_directory(tmp_path: str) -> Tuple[str, str, str, str]:
    """Fixture that sets up a mock infrastructure directory structure for testing purposes.

    Args:
        tmp_path (str): The temporary directory path provided by pytest.

    Yields:
        Tuple[str, str, str, str]: A tuple containing the paths to the infrastructure directory, main module directory, and submodule directories.
        submodule 1 directory, and submodule 2 directory.
    """
    os.chdir(tmp_path)

    infrastructure_dir = os.path.join(os.getcwd(), "infrastructure")
    os.mkdir(infrastructure_dir)

    main_module_dir = os.path.join(infrastructure_dir, "test_resource")
    os.mkdir(main_module_dir)

    main_module_files = [".gitignore", ".terraform.lock.hcl"]
    for file in main_module_files:
        file_path = os.path.join(main_module_dir, file)
        with open(file_path, "a"):
            ...

    submodule_1_dir = os.path.join(main_module_dir, "test_submodule_1")
    submodule_2_dir = os.path.join(main_module_dir, "test_submodule_2")
    os.mkdir(submodule_1_dir)
    os.mkdir(submodule_2_dir)

    submodule_1_files = ["test_file_1.tf"]
    for file in submodule_1_files:
        file_path = os.path.join(submodule_1_dir, file)
        with open(file_path, "a"):
            ...

    submodule_2_files = ["test_file_2.yaml", "test_file_3.tpl"]
    for file in submodule_2_files:
        file_path = os.path.join(submodule_2_dir, file)
        with open(file_path, "w"):
            ...

    yield infrastructure_dir, main_module_dir, submodule_1_dir, submodule_2_dir

    # Clean up the created directories and files after the test
    shutil.rmtree(infrastructure_dir)
