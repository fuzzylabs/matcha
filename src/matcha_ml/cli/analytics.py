"""Matcha CLI for opting out/in of collecting analytics."""
import typer
from rich import print

from matcha_ml.services.global_parameters_service import GlobalParameters

# create a typer app to group all analytics subcommands
app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)


@app.command()
def opt_out() -> None:
    """Disable the collection of anonymous usage data."""
    print(
        "Data collection has been turned off and no data will be collected - you can turn this back on by running the command: 'matcha analytics opt-in'"
    )
    GlobalParameters().analytics_opt_out = True


@app.command()
def opt_in() -> None:
    """Enable the collection of anonymous usage data (enabled by default)."""
    print(
        "Thank you for enabling data collection, this helps us improve matcha and anonymously understand how people are using the tool."
    )
    GlobalParameters().analytics_opt_out = False
