import asyncio
from pathlib import Path

import typer

from memorymarker.document_providers.omnivore import Omnivore
from memorymarker.main_cli import TimestampHandler
from memorymarker.persist_questions.markdown import write_qa_prompt_to_md
from memorymarker.question_generator.question_generator import (
    highlights_to_questions,
    initialize_model,
)

from .cli.document_selector import select_documents


def main(
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
    output_dir.mkdir(exist_ok=True, parents=True)
    last_run_timestamper = TimestampHandler(output_dir / ".memorymarker")
    last_run_timestamp = last_run_timestamper.get_timestamp()

    typer.echo("Fetching documents")
    documents = Omnivore().get_documents().filter(lambda _: len(_.highlights) > 0)

    if select:
        documents = select_documents(documents)

    typer.echo("Processing to highlights")
    highlights = documents.map(lambda _: _.get_highlights()).flatten()

    if only_new:
        if not last_run_timestamp:
            typer.echo("No last run timestamp found, exiting")
            last_run_timestamper.update_timestamp()
            return

        typer.echo(f"Last run at UTC {last_run_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        highlights = highlights.filter(lambda _: _.updated_at > last_run_timestamp)
        last_run_timestamper.update_timestamp()

        if highlights.count() == 0:
            typer.echo("No new highlights since last run")
            return

        typer.echo(f"Received {highlights.count()} new highlights")

    typer.echo("Generating questions from highlights...")
    questions = asyncio.run(
        highlights_to_questions(
            model=initialize_model("gpt-3.5-turbo"), highlights=highlights.to_list()[-max_n:]
        )
    )

    typer.echo("Writing questions to markdown...")
    for question in questions:
        typer.echo(f"Writing question to {question.title}")
        write_qa_prompt_to_md(save_dir=output_dir, prompt=question)
