"""Destroy CLI."""
from matcha_ml.cli.ui_primitives.ui_functions import print_step_success
from matcha_ml.templates.run_template import TerraformService


def destroy_resources() -> None:
    """Destroy resources."""
    # create a terraform service
    tfs = TerraformService()

    # deprovision the resources
    tfs.deprovision()

    print_step_success("Destroying resources is complete!")
