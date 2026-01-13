# src/osf_downloader/cli.py

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .download import OSFDownloader, OSFError

app = typer.Typer(help="Download data from OSF.")
console = Console()


@app.command()
def download(
    project_id: str = typer.Argument(..., help="OSF project ID"),
    save_path: Path = typer.Argument(..., help="Local output path"),
    file_path: Optional[str] = typer.Argument(None, help="Path inside OSF storage"),
):
    downloader = OSFDownloader(console=console)

    try:
        downloader.download(project_id, save_path, file_path)
    except OSFError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


def main() -> None:
    app()
