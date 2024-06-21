import asyncio
import datetime as dt
import logging
import os
from dataclasses import dataclass
from pathlib import Path

import coloredlogs
import pytz
import typer
from dotenv import load_dotenv
from iterpy.iter import Iter

from memorymarker.document_providers.omnivore import Omnivore
from memorymarker.persister.markdown import highlight_group_to_file
from memorymarker.question_generator.chunker import chunk_highlights
from memorymarker.question_generator.completers.anthropic_completer import (
    AnthropicCompleter,
)
from memorymarker.question_generator.completers.openai_completer import (
    OpenAICompleter,
    OpenAIModelCompleter,
)
from memorymarker.question_generator.flows.question_flow import QuestionFlow
from memorymarker.question_generator.qa_responses import QAResponses
from memorymarker.question_generator.steps.qa_extractor import QuestionExtractor
from memorymarker.question_generator.steps.qa_generation import QuestionGenerator
from memorymarker.question_generator.steps.question_wikilinker import QuestionWikilinker
from memorymarker.question_generator.steps.reasoning import Reasoning

app = typer.Typer(no_args_is_help=True)

from importlib.metadata import version


def get_api_key_from_env(env_var: str) -> str | None:
    return os.getenv(env_var, None)


@dataclass(frozen=True)
class TimestampRepository:
    """Writes and gets a timestamp for syncing."""

    filepath: Path

    def update_timestamp(self) -> None:
        if not self.filepath.exists():
            self.filepath.touch()

        self.filepath.write_text(dt.datetime.now(pytz.UTC).isoformat())

    def get_timestamp(self) -> dt.datetime:
        """Returns the last run timestamp or a value far in the past if it doesn't exist."""
        try:
            return dt.datetime.fromisoformat(self.filepath.read_text())
        except FileNotFoundError:
            logging.info(
                "No last run timestamp found, generating questions for all highlights"
            )
            return dt.datetime(1970, 1, 1, tzinfo=pytz.UTC)


@app.command()  # type: ignore
def typer_cli(
    omnivore_api_key: str = typer.Argument(
        help="Omnivore API key", envvar="OMNIVORE_API_KEY"
    ),
    openai_api_key: str = typer.Argument(
        help="OpenAI API key", envvar="OPENAI_API_KEY"
    ),
    anthropic_api_key: str = typer.Argument(
        help="Anthropic API key", envvar="ANTHROPIC_API_KEY"
    ),
    output_dir: Path = typer.Argument(  # noqa: B008 # type: ignore
        Path("/output"),
        help="Directory to save the generated questions to",
        file_okay=False,
        dir_okay=True,
        writable=True,
    ),
    max_n: int = typer.Argument(
        help="Maximum number of questions in total", envvar="MAX_N"
    ),
    only_new: bool = typer.Option(
        True, help="Only generate questions from highlights since last run"
    ),
) -> None:
    output_dir.mkdir(exist_ok=True, parents=True)

    logging.info(f"MemoryMarker version {version('memorymarker')}")

    logging.info("Fetching documents")
    documents = (
        Omnivore(omnivore_api_key)
        .get_documents()
        .filter(lambda _: len(_.highlights) > 0)
    )

    # Extract highlights from documents
    highlights = documents.map(lambda _: _.get_highlights()).flatten()
    last_run_timestamper = TimestampRepository(output_dir / ".memorymarker")

    if only_new:
        last_run_timestamp = last_run_timestamper.get_timestamp()
        logging.info(
            f"Last run at UTC {last_run_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        highlights = highlights.filter(lambda _: _.updated_at > last_run_timestamp)

    if highlights.count() == 0:
        logging.info("No new highlights since last run")
        return
    logging.info(f"Received {highlights.count()} new highlights")
    logging.info(
        f"max_n is set to {max_n}, so processing {min(max_n, highlights.count())} highlights"
    )

    # Chunk highlights for better reasoning and fewer duplicate questions
    logging.info("Generating questions from highlights...")
    chunked_highlights = (
        highlights.groupby(lambda _: _.source_document.title)
        .map(lambda _: chunk_highlights(_, 5))
        .flatten()
    )

    # Generate questions
    base_completer = AnthropicCompleter(
        api_key=anthropic_api_key, model="claude-3-opus-20240229"
    )
    questions = asyncio.run(
        QuestionFlow(
            name="simplified_reasoning",
            steps=(
                Reasoning(completer=base_completer),
                QuestionGenerator(completer=base_completer, n_questions=(1, 5)),
                QuestionExtractor(
                    completer=OpenAIModelCompleter(
                        api_key=openai_api_key,
                        model="gpt-3.5-turbo",
                        response_model=QAResponses,  # type: ignore
                    )
                ),
                QuestionWikilinker(
                    completer=OpenAICompleter(
                        api_key=os.getenv("OPENAI_API_KEY", "No OPENAI_API"),
                        model="gpt-4-turbo-preview",
                    )
                ),
            ),
        )(chunked_highlights[0:max_n])
    )

    # Write to disk
    logging.info("Writing questions to markdown...")
    (
        Iter(questions)
        .groupby(lambda _: _.source_document.title)
        .map(lambda _: highlight_group_to_file(output_dir, _))
    )
    last_run_timestamper.update_timestamp()


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
