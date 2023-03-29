""""""
from rich import print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

err_console = Console(stderr=True)

SPINNER = "dots"


def print_status(status: str):
    # print a grey status message
    print(f"[white]{status}[/white]")


def print_step_success(status: str):
    # green and bold status message for step completion
    print(f"[green bold]{status}[/green bold]")


def print_substep_success(status: str):
    # green status message when substep was completed.
    print(f"[green]{status}[/green]")


def print_confirm_message(status: str, is_list: bool):
    # yellow message for confirmation.
    if is_list:
        lines = status.split("\n")
        for i, line in enumerate(lines):
            if ":" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    name = parts[0].strip()
                    value = parts[1].strip()
                    lines[i] = f"{name}: [yellow]{value}[/yellow]"
        output = "\n".join(lines)
        print(output)
    else:
        print(f"[yellow]{status}[/yellow]")


def print_error_message(status: str):
    err_console.print(status, style="blink")


def show_spinner(status: str):
    # show a spinner and a status message for a long running task
    with Progress(
        SpinnerColumn(spinner_name=SPINNER),
        TimeElapsedColumn(),
    ) as progress:
        progress.add_task(description=status, total=None)
