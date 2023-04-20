"""Destroy CLI."""
from matcha_ml.cli.ui.print_messages import print_status
from matcha_ml.cli.ui.status_message_builders import build_step_success_status
from matcha_ml.services.terraform_service import TerraformService
from matcha_ml.templates.run_template import deprovision


def destroy_resources() -> None:
    """Destroy resources."""
    # create a terraform service
    tfs = TerraformService()

    # deprovision the resources
    deprovision(tfs)

    print_status(build_step_success_status("Destroying resources is complete!"))
