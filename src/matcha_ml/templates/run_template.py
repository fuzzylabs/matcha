"""Run terraform templates to provision and deprovision resources."""
import json
import os

import typer

from matcha_ml.cli.ui.emojis import Emojis
from matcha_ml.cli.ui.print_messages import print_error, print_json, print_status
from matcha_ml.cli.ui.spinner import Spinner
from matcha_ml.cli.ui.status_message_builders import (
    build_resource_confirmation,
    build_status,
    build_substep_success_status,
)
from matcha_ml.errors import MatchaTerraformError
from matcha_ml.services.terraform_service import TerraformService

OUTPUTS = {
    "mlflow-tracking-url",
    "zenml-storage-path",
    "zenml-connection-string",
    "k8s-context",
    "azure-container-registry",
    "azure-registry-name",
    "zen-server-url",
    "zen-server-username",
    "zen-server-password",
    "seldon-workloads-namespace",
    "seldon-base-url",
}

SPINNER = "dots"


def _check_terraform_installation(tfs: TerraformService) -> None:
    """Checks if terraform is installed on the host system.

    Args:
        tfs (TerraformService): the Terraform service interface.

    Raises:
        typer.Exit: if terraform is not installed.
    """
    if not tfs.check_installation():
        print_error(f"{Emojis.CROSS.value} Terraform is not installed")
        print_error(
            "Terraform is required for to run and was not found installed on your machine."
            "Please visit https://learn.hashicorp.com/tutorials/terraform/install-cli to install it."
        )
        raise typer.Exit()


def _validate_terraform_config(tfs: TerraformService) -> None:
    """Validate the configuration used for creating resources.

    Args:
        tfs (TerraformService): the Terraform service interface.

    Raises:
        typer.Exit: if `terraform.tfvars.json` file not found in current directory.
    """
    if not tfs.validate_config():
        print_error(
            "The file terraform.tfvars.json was not found in the "
            f"current directory at {tfs.config.var_file}. Please "
            "verify if it exists."
        )
        raise typer.Exit()


def _is_approved(verb: str) -> bool:
    """Get approval from user to modify resources on cloud.

    Args:
        verb (str): the verb to use in the approval message.

    Returns:
        bool: True if user approves, False otherwise.
    """
    summary_message = build_resource_confirmation(
        header=f"The following resources will be {verb}ed",
        resources=[
            ("Resource group", "A resource group"),
            ("Azure Kubernetes Service (AKS)", "A kubernetes cluster"),
            (
                "Two Azure Storage Container",
                "A storage container for experiment tracking artifacts and a second for model training artifacts",
            ),
            (
                "Seldon Core",
                "A framework for model deployment on top of a kubernetes cluster",
            ),
            (
                "Azure Container Registry",
                "A container registry for storing docker images",
            ),
            ("ZenServer", "A zenml server required for remote orchestration"),
        ],
        footer=f"{verb.capitalize()}ing the resources may take up to 20 minutes. May we suggest you to grab a cup of {Emojis.MATCHA.value}?",
    )

    print_status(summary_message)
    return typer.confirm(f"Are you happy for '{verb}' to run?")


def _initialise_terraform(tfs: TerraformService) -> None:
    """Run terraform init to initialise Terraform .

    Args:
        tfs (TerraformService): the Terraform service interface.

    Raises:
        MatchaTerraformError: if 'terraform init' failed.
    """
    previous_temp_dir = tfs.get_previous_temp_dir()
    if previous_temp_dir.exists():
        # this directory gets created after a successful init command
        print_status(
            build_status(
                f"matcha {Emojis.MATCHA.value} has already been initialised. Skipping this step..."
            )
        )

    else:
        print_status(
            build_status(
                f"\n{Emojis.WAITING.value} Brewing matcha {Emojis.MATCHA.value}...\n"
            )
        )

        with Spinner("Initializing"):
            ret_code, _, err = tfs.init()

        if ret_code != 0:
            print_error("The command 'terraform init' failed.")
            raise MatchaTerraformError(tf_error=err)

        # Create a directory to avoid running init multiple times
        previous_temp_dir.mkdir(parents=True, exist_ok=True)

        print_status(
            build_substep_success_status(
                f"{Emojis.CHECKMARK.value} Matcha {Emojis.MATCHA.value} initialised!\n"
            )
        )


def _check_matcha_directory_exists(tfs: TerraformService) -> None:
    """Checks if .matcha directory exists within the current working directory.

    Args:
        tfs (TerraformService): the Terraform service interface.

    Raises:
        typer.Exit: if the .matcha directory does not exist.
        typer.Exit: if the .matcha directory does not contain the required files to deploy resources.
    """
    if not tfs.check_matcha_directory_exists():
        print_error(
            f"Error, the .matcha directory does not exist in {os.getcwd()} . Please ensure you are trying to destroy resources that you have provisioned in the current working directory."
        )
        raise typer.Exit()

    if not tfs.check_matcha_directory_integrity():
        print_error(
            "Error, the .matcha directory does not contain files relating to deployed resources. Please ensure you are trying to destroy resources that you have provisioned in the current working directory."
        )
        raise typer.Exit()


def _apply_terraform(tfs: TerraformService) -> None:
    """Run terraform apply to create resources on cloud.

    Args:
        tfs (TerraformService): the Terraform service interface.

    Raises:
        MatchaTerraformError: if 'terraform apply' failed.
    """
    with Spinner("Applying"):
        ret_code, _, err = tfs.apply()

    if ret_code != 0:
        raise MatchaTerraformError(tf_error=err)

    print_status(
        build_substep_success_status(
            f"{Emojis.CHECKMARK.value} Your environment has been provisioned!\n"
        )
    )
    state_file = tfs.get_state_file_dir()
    state_outputs = {
        name: tfs.terraform_client.output(name, full_value=True) for name in OUTPUTS
    }

    # dump specific terraform output to state file
    with open(state_file, "w") as fp:
        json.dump(state_outputs, fp, indent=4)

    print_status(build_status("Here are the endpoints for what's been provisioned"))
    # print terraform output from state file
    with open(state_file) as fp:
        print_json(fp.read())


def _destroy_terraform(tfs: TerraformService) -> None:
    """Destroy the provisioned resources.

    Args:
        tfs (TerraformService): the Terraform service interface.

    Raises:
        MatchaTerraformError: if 'terraform destroy' failed.
    """
    print()
    print_status(build_status(f"{Emojis.WAITING.value} Destroying your resources..."))
    print()
    with Spinner("Destroying"):
        ret_code, _, err = tfs.destroy()

    if ret_code != 0:
        raise MatchaTerraformError(tf_error=err)


def provision(tfs: TerraformService) -> None:
    """Provision resources required for the deployment.

    Args:
        tfs (TerraformService): the Terraform service interface.

    Raises:
        typer.Exit: if approval is not given by user.
    """
    _check_terraform_installation(tfs)
    _validate_terraform_config(tfs)

    if _is_approved(verb="provision"):
        _initialise_terraform(tfs)
        _apply_terraform(tfs)
    else:
        print_status(
            build_status(
                "You decided to cancel - if you change your mind, then run 'matcha provision' again."
            )
        )
        raise typer.Exit()


def deprovision(tfs: TerraformService) -> None:
    """Destroy the provisioned resources.

    Args:
        tfs (TerraformService): the Terraform service interface.

    Raises:
        typer.Exit: if approval is not given by user.
    """
    _check_terraform_installation(tfs)

    _check_matcha_directory_exists(tfs)

    if _is_approved(verb="destroy"):
        _destroy_terraform(tfs)
    else:
        print_status(
            build_status(
                "You decided to cancel - your resources will remain active! If you change your mind, then run 'matcha destroy' again."
            )
        )
        raise typer.Exit()
