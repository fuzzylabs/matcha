"""Test suite to test the azure template."""
import os
import shutil
import tempfile

import pytest

from matcha_ml.templates import AzureTemplate


@pytest.fixture
def azure_template() -> AzureTemplate:
    """Azure template object for testing.

    Returns:
        AzureTemplate: the Azure template.
    """
    return AzureTemplate()


@pytest.fixture
def temp_directory() -> str:
    """Temporary testing directory.

    Returns:
        str: Location of the directory.

    Yields:
        Iterator[str]: Location of the directory.
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_empty_directory_except_files(temp_directory: str) -> None:
    """Test the 'empty_directory_except_files' function.

    Args:
        temp_directory (str): Temporary directory path for testing.
    """
    # Create some files and directories in the temporary directory
    with open(os.path.join(temp_directory, "file1.txt"), "w") as f:
        f.write("Content of file1")
    with open(os.path.join(temp_directory, "file2.txt"), "w") as f:
        f.write("Content of file2")

    # Call the function to empty the directory except for file2.txt
    AzureTemplate.empty_directory_except_files(
        temp_directory, except_files=["file2.txt"]
    )

    assert not os.path.exists(os.path.join(temp_directory, "file1.txt"))
    assert os.path.exists(os.path.join(temp_directory, "file2.txt"))


def test_concatenate_files(temp_directory: str) -> None:
    """Test the 'concatenate_files' function.

    Args:
        temp_directory (str): Temporary directory path for testing.
    """
    source_file = os.path.join(temp_directory, "source.txt")
    target_file = os.path.join(temp_directory, "target.txt")

    # Create source and target files with some content
    with open(source_file, "w") as source:
        source.write("Source file content")
    with open(target_file, "w") as target:
        target.write("Target file content")

    # Call the function to concatenate source_file to target_file
    AzureTemplate.concatenate_files(source_file, target_file)

    # Check if the contents of target_file have been updated
    with open(target_file) as target:
        assert target.read() == "Target file contentSource file content"


def test_recursively_copy_files(temp_directory: str) -> None:
    """Test the 'recursively_copy_files' function.

    Args:
        temp_directory (str): Temporary directory path for testing.
    """
    source_dir = os.path.join(temp_directory, "source")
    target_dir = os.path.join(temp_directory, "target")

    # Create some files and directories in the source directory
    os.mkdir(source_dir)
    os.mkdir(os.path.join(source_dir, "subfolder"))
    with open(os.path.join(source_dir, "file1.txt"), "w") as f:
        f.write("Content of file1")
    with open(os.path.join(source_dir, "subfolder", "file2.txt"), "w") as f:
        f.write("Content of file2")

    # Call the function to copy files from source_dir to target_dir
    AzureTemplate.recursively_copy_files(source_dir, target_dir)

    # Check if the files and directories have been copied correctly
    assert os.path.exists(os.path.join(target_dir, "file1.txt"))
    assert os.path.exists(os.path.join(target_dir, "subfolder", "file2.txt"))

    # Check if the content of 'file1.txt' and 'file2.txt' has been copied correctly
    with open(os.path.join(target_dir, "file1.txt")) as f:
        assert f.read() == "Content of file1"
    with open(os.path.join(target_dir, "subfolder", "file2.txt")) as f:
        assert f.read() == "Content of file2"


def test_empty_directory_except_files_error_handling(
    temp_directory: str, capsys
) -> None:
    """Test error handling in AzureTemplate.empty_directory_except_files function.

    Args:
        temp_directory (str): The path to a temporary directory.
        capsys: Pytest fixture for capturing stdout and stderr.
    """
    # Run the function that raises an exception
    AzureTemplate.empty_directory_except_files("nonexistent_directory", [])

    # Capture the output (stdout and stderr)
    captured = capsys.readouterr()

    # Check if the error message is present in the captured output
    assert "Error while emptying directory" in captured.err


def test_concatenate_files_error_handling(temp_directory: str, capsys) -> None:
    """Test error handling in AzureTemplate.concatenate_files function.

    Args:
        temp_directory (str): The path to a temporary directory.
        capsys: Pytest fixture for capturing stdout and stderr.
    """
    os.path.join(temp_directory, "source.txt")
    target_file = os.path.join(temp_directory, "target.txt")

    # Run the function that raises an exception
    AzureTemplate.concatenate_files("nonexistent_file.txt", target_file)

    # Capture the output (stdout and stderr)
    captured = capsys.readouterr()

    # Check if the error message is present in the captured output
    assert "Error while concatenating files:" in captured.err


def test_recursively_copy_files_error_handling_directory_not_exist(
    temp_directory: str, capsys
) -> None:
    """Test error handling in AzureTemplate.recursively_copy_files function when source directory does not exist.

    Args:
        temp_directory (str): The path to a temporary directory.
        capsys: Pytest fixture for capturing stdout and stderr.
    """
    # Run the function that raises an exception
    AzureTemplate.recursively_copy_files("nonexistent_source", "target")

    # Capture the output (stdout and stderr)
    captured = capsys.readouterr()

    # Check if the error message is present in the captured output
    assert (
        "Error while copying files: [Errno 2] No such file or directory:"
        in captured.err
    )


def test_recursively_copy_files_error_handling_target_dir_exists(
    temp_directory: str, capsys
) -> None:
    """Test error handling in AzureTemplate.recursively_copy_files function when the target directory cannot be created.

    Args:
        temp_directory (str): The path to a temporary directory.
        capsys: Pytest fixture for capturing stdout and stderr.
    """
    # Create a file with the same name as the target directory
    target_dir_as_file = os.path.join(temp_directory, "target")
    with open(target_dir_as_file, "w") as file:
        file.write("content")

    # Run the function that raises an exception
    AzureTemplate.recursively_copy_files(temp_directory, target_dir_as_file)

    # Capture the output (stdout and stderr)
    captured = capsys.readouterr()

    # Check if the error message is present in the captured output
    assert "Error while copying files:" in captured.err


def test_recursively_copy_files_error_handling_permission_error(
    temp_directory: str, capsys
) -> None:
    """Test error handling in AzureTemplate.recursively_copy_files function when a source file cannot be copied due to permission error.

    Args:
        temp_directory (str): The path to a temporary directory.
        capsys: Pytest fixture for capturing stdout and stderr.
    """
    source_file = os.path.join(temp_directory, "source.txt")
    with open(source_file, "w") as file:
        file.write("content")

    # Create a read-only target directory
    target_dir = os.path.join(temp_directory, "target")
    os.makedirs(target_dir, exist_ok=True)
    os.chmod(target_dir, 0o444)  # Make it read-only

    # Run the function that raises an exception
    AzureTemplate.recursively_copy_files(temp_directory, target_dir)

    # Capture the output (stdout and stderr)
    captured = capsys.readouterr()

    # Check if the error message is present in the captured output
    assert "Permission denied" in captured.err
