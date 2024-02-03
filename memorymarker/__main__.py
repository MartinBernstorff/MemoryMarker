import asyncio
import datetime as dt
import os
from pathlib import Path

import pytz
import typer

from memorymarker.highlight_providers.omnivore import Omnivore
from memorymarker.persist_questions.markdown import write_qa_prompt_to_md
from memorymarker.question_generator.question_generator import (
    highlights_to_questions,
    initialize_model,
)

app = typer.Typer()


def get_api_key_from_env(env_var: str) -> str | None:
    return os.getenv(env_var, None)


@app.command()
def typer_cli(
    output_dir: Path = typer.Argument(
        Path("questions"), help="Directory to save the generated questions to"
    ),
    max_n: int = typer.Argument(
        1, help="Maximum number of questions to generate from highlights"
    ),
    since_date: dt.datetime = typer.Option(
        dt.datetime.now(pytz.timezone("UTC")) - dt.timedelta(days=7),
        help="Date to start gathering highlights from",
    ),
) -> None:
    typer.echo("Getting highlights from Omnivore...")
    highlights = Omnivore().get_highlights().filter(lambda h: h.updated_at > since_date)

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
