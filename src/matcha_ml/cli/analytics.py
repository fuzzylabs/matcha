"""Matcha CLI for opting out/in of collecting analytics."""
from rich import print
import typer

from matcha_ml.services.global_parameters_service import GlobalParameters

# create a typer app to group all analytics subcommands
app = typer.Typer()


@app.command()
def opt_out():
    """Opt-out of collecting analytics."""
    return GlobalParameters().opt_out_of_analytics()


@app.command()
def opt_in():
    """Opt-in for collecting analytics."""
    print(
        "Thank you for allowing matcha to collect analytics data. This is very helpful!"
    )
    return GlobalParameters().opt_in_to_analytics()
