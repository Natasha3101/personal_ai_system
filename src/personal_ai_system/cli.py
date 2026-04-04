"""Console script for personal_ai_system."""

import typer
from rich.console import Console

from personal_ai_system import utils

app = typer.Typer()
console = Console()


@app.command()
def main() -> None:
    """Console script for personal_ai_system."""
    console.print("Replace this message by putting your code into personal_ai_system.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
