"""Provision CLI."""
from typing import Tuple

import typer

from matcha_ml.cli._validation import prefix_typer_callback, region_typer_callback

# create a typer app to group all provision subcommands
app = typer.Typer()


def fill_provision_variables(
    location: str,
    prefix: str,
    password: str,
) -> Tuple[str, str, str]:
    """Prompt for the provision variables if they were not provided.

    Args:
        location (str): Azure location in which all resources will be provisioned, or empty string to fill in.
        prefix (str): Prefix used for all resources, or empty string to fill in.
        password (str): Password for ZenServer, or empty string to fill in.

    Returns:
        Tuple[str, str, str]: A tuple of location, prefix and password which were filled in
    """
    if not location:
        location = typer.prompt(
            default=None,
            text="What region should your resources be provisioned in (e.g., 'ukwest')?",
            value_proc=region_typer_callback,
        )
    if not prefix:
        prefix = typer.prompt(
            text="Your resources need a name (an alphanumerical prefix; 3-11 character limit), what should matcha call them?",
            default="matcha",
            value_proc=prefix_typer_callback,
        )
    if not password:
        password = typer.prompt(
            default=None,
            text="Set a password for your deployment server",
            confirmation_prompt=True,
            hide_input=True,
        )

    return location, prefix, password
