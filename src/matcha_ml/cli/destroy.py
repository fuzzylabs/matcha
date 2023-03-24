"""Destroy CLI."""
from matcha_ml.templates.run_template import TerraformService


def destroy_resources() -> None:
    """Destroy resources."""
    # create a terraform service
    tfs = TerraformService()

    # deprovision the resources
    tfs.deprovision()
