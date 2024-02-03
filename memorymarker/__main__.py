import asyncio
import datetime as dt
import os
from dataclasses import dataclass
from pathlib import Path

import pytz
import typer

from memorymarker.highlight_providers.omnivore import Omnivore
from memorymarker.persist_questions.markdown import write_qa_prompt_to_md
from memorymarker.question_generator.question_generator import (
    highlights_to_questions,
    initialize_model,
)

app = typer.Typer(no_args_is_help=True)


def get_api_key_from_env(env_var: str) -> str | None:
    return os.getenv(env_var, None)


@dataclass(frozen=True)
class TimestampHandler:
    filepath: Path

    def update_timestamp(self) -> None:
        self.filepath.write_text(dt.datetime.now(pytz.UTC).isoformat())

    def get_timestamp(self) -> dt.datetime:
        return dt.datetime.fromisoformat(self.filepath.read_text())


@app.command()
def typer_cli(
    output_dir: Path = typer.Argument(
        Path("questions"), help="Directory to save the generated questions to"
    ),
    max_n: int = typer.Argument(
        1, help="Maximum number of questions to generate from highlights"
    ),
    only_new: bool = typer.Option(
        True, help="Only generate questions from highlights since last run"
    ),
) -> None:
    last_run_timestamper = TimestampHandler(output_dir / ".memorymarker")
    typer.echo(
        f"Last run at UTC {last_run_timestamper.get_timestamp().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    typer.echo("Fetching new highlights...")
    highlights = Omnivore().get_highlights()

    if only_new:
        highlights = highlights.filter(
            lambda _: _.updated_at > last_run_timestamper.get_timestamp()
        )
        last_run_timestamper.update_timestamp()

        if highlights.count() == 0:
            typer.echo("No new highlights since last run")
            return

        typer.echo(f"Received {highlights.count()} new highlights")

    typer.echo("Generating questions from highlights...")
    questions = asyncio.run(
        highlights_to_questions(
            model=initialize_model("gpt-3.5-turbo"),
            highlights=highlights.to_list()[0:max_n],
        )
    )

    typer.echo("Writing questions to markdown...")
    for question in questions:
        write_qa_prompt_to_md(save_dir=output_dir, prompt=question)


if __name__ == "__main__":
    app()
