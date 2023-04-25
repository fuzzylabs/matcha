"""Destroy CLI."""
from matcha_ml.cli.ui.print_messages import print_status
from matcha_ml.cli.ui.status_message_builders import build_step_success_status
from matcha_ml.templates.run_template import TemplateRunner


def destroy_resources() -> None:
    """Destroy resources."""
    # create a runner for deprovisioning resource with Terraform service.
    template_runner = TemplateRunner()

    # deprovision the resources
    template_runner.deprovision()

    print_status(build_step_success_status("Destroying resources is complete!"))
