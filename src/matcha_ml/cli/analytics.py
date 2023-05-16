"""Matcha CLI for opting out/in of collecting analytics."""
import typer
from rich import print

from matcha_ml.services.global_parameters_service import GlobalParameters

# create a typer app to group all analytics subcommands
app = typer.Typer()


@app.command()
def opt_out() -> None:
    """Disable the collection of anonymous usage data."""
    print(
        "Data collection has been turned off and no data will be collected - you can turn this back on by running the command: matcha analytics opt-in"
    )
    return GlobalParameters().opt_out_of_analytics()


@app.command()
def opt_in() -> None:
    """Enable the collection of anonymous usage data (enabled by default)."""
    print(
        "Thank you for enabling data collection, this helps us improve matcha and anonymously understand how people are using the tool."
    )
    return GlobalParameters().opt_in_to_analytics()
