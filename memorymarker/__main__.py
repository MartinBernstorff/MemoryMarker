import asyncio
import datetime as dt
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import coloredlogs
import pytz
import typer
from dotenv import load_dotenv
from iterpy.iter import Iter

from memorymarker.cli.document_selector import select_documents
from memorymarker.document_providers.omnivore import Omnivore
from memorymarker.persist_questions.markdown import highlight_group_to_file
from memorymarker.question_generator.completers.anthropic_completer import (
    AnthropicCompleter,
)
from memorymarker.question_generator.completers.openai_completer import (
    OpenAICompleter,
    OpenAIModelCompleter,
)
from memorymarker.question_generator.flows.question_flow import QuestionFlow
from memorymarker.question_generator.main import chunk_highlights
from memorymarker.question_generator.qa_responses import QAResponses
from memorymarker.question_generator.steps.qa_extractor import QuestionExtractionStep
from memorymarker.question_generator.steps.qa_generation import QuestionGenerationStep
from memorymarker.question_generator.steps.question_wikilinker import (
    QuestionWikilinkerStep,
)
from memorymarker.question_generator.steps.reasoning import ReasoningStep

app = typer.Typer(no_args_is_help=True)

from importlib.metadata import version


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


def sleep_and_run(sleep_time: int, run_func: Callable[[], None]) -> None:
    time.sleep(sleep_time)
    run_func()


@app.command()  # type: ignore
def typer_cli(
    omnivore_api_key: str = typer.Option(
        None, help="Omnivore API key", envvar="OMNIVORE_API_KEY"
    ),
    openai_api_key: str = typer.Option(
        None, help="Anthropic API key", envvar="OPENAI_API_KEY"
    ),
    anthropic_api_key: str = typer.Option(
        None, help="Anthropic API key", envvar="ANTHROPIC_API_KEY"
    ),
    output_dir: Path = typer.Argument(  # noqa: B008 # type: ignore
        Path("questions"),
        help="Directory to save the generated questions to",
        file_okay=False,
        dir_okay=True,
        writable=True,
    ),
    run_every: int = typer.Option(
        None, help="How often to run the script in seconds", envvar="RUN_EVERY"
    ),
    max_n: int = typer.Argument(
        1, help="Maximum number of questions to generate from highlights"
    ),
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

    logging.info(f"MemoryMarker version {version('memorymarker')}")
    logging.info("Fetching documents")
    documents = (
        Omnivore(omnivore_api_key)
        .get_documents()
        .filter(lambda _: len(_.highlights) > 0)
    )

    if select:
        documents = select_documents(documents)

    logging.info("Processing to highlights")
    highlights = documents.map(lambda _: _.get_highlights()).flatten()

    if only_new:
        if not last_run_timestamp:
            logging.info(
                "No last run timestamp found, generating questions for all highlights"
            )
            last_run_timestamp = dt.datetime(1970, 1, 1, tzinfo=pytz.UTC)

        logging.info(
            f"Last run at UTC {last_run_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        highlights = highlights.filter(lambda _: _.updated_at > last_run_timestamp)

        if highlights.count() == 0:
            logging.info("No new highlights since last run")
            if not run_every:
                return

    logging.info(f"Received {highlights.count()} new highlights")

    logging.info("Generating questions from highlights...")
    base_completer = AnthropicCompleter(
        api_key=anthropic_api_key, model="claude-3-opus-20240229"
    )
    chunked_highlights = (
        highlights.groupby(lambda _: _.source_document.title)
        .map(lambda _: chunk_highlights(_, 5))
        .flatten()
    )
    questions = asyncio.run(
        QuestionFlow(
            _name="simplified_reasoning",
            steps=(
                ReasoningStep(completer=base_completer),
                QuestionGenerationStep(completer=base_completer, n_questions=(1, 5)),
                QuestionExtractionStep(
                    completer=OpenAIModelCompleter(
                        api_key=openai_api_key,
                        model="gpt-3.5-turbo",
                        response_model=QAResponses,  # type: ignore
                    )
                ),
                QuestionWikilinkerStep(
                    completer=OpenAICompleter(
                        api_key=os.getenv("OPENAI_API_KEY", "No OPENAI_API"),
                        model="gpt-4-turbo-preview",
                    )
                ),
            ),
        )(chunked_highlights[0:max_n])
    )

    logging.info("Writing questions to markdown...")

    highlight_groups = Iter(questions[0:max_n]).groupby(
        lambda _: _.source_document.title
    )
    for group in highlight_groups:
        highlight_group_to_file(output_dir, group)

    last_run_timestamper.update_timestamp()
    if run_every:
        logging.info(f"Running every {run_every} seconds")
        time.sleep(run_every)
        logging.info("Running again")
        typer_cli(
            omnivore_api_key=omnivore_api_key,
            output_dir=output_dir,
            run_every=run_every,
            max_n=max_n,
            only_new=only_new,
            select=select,
        )


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y/&m/%d %H:%M:%S",
        filename="main.log",
    )
    coloredlogs.install(level="DEBUG")  # type: ignore
    app()
