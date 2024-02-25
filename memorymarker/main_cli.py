import datetime as dt
import os
from dataclasses import dataclass
from pathlib import Path

import pytz
import typer

from memorymarker.main import main

app = typer.Typer(no_args_is_help=True)


def get_api_key_from_env(env_var: str) -> str | None:
    return os.getenv(env_var, None)


@dataclass(frozen=True)
class TimestampHandler:
    filepath: Path

    def update_timestamp(self) -> None:
        if not self.filepath.exists():
            self.filepath.touch()

        self.filepath.write_text(dt.datetime.now(pytz.UTC).isoformat())

    def get_timestamp(self) -> dt.datetime | None:
        try:
            return dt.datetime.fromisoformat(self.filepath.read_text())
        except FileNotFoundError:
            return None


@app.command()  # type: ignore
def typer_cli(
    output_dir: Path = typer.Argument(  # noqa: B008 # type: ignore
        Path("questions"),
        help="Directory to save the generated questions to",
        file_okay=False,
        dir_okay=True,
        writable=True,
    ),
    max_n: int = typer.Argument(1, help="Maximum number of questions to generate from highlights"),
    only_new: bool = typer.Option(
        True, help="Only generate questions from highlights since last run"
    ),
    select: bool = typer.Option(
        False, help="Prompt to select which documents to generate questions from"
    ),
) -> None:
    main(output_dir=output_dir, max_n=max_n, only_new=only_new, select=select)


if __name__ == "__main__":
    app()
