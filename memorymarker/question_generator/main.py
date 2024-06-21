import asyncio
import logging
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

import coloredlogs
from iterpy.iter import Iter
from joblib import Memory

from memorymarker.document_providers.omnivore import Omnivore
from memorymarker.question_generator.completers.anthropic_completer import (
    AnthropicCompleter,
)
from memorymarker.question_generator.completers.openai_completer import (
    OpenAICompleter,
    OpenAIModelCompleter,
)
from memorymarker.question_generator.example_repo_airtable import (
    AirtableExampleRepo,
    PipelineHighlightIdentity,
    update_repository,
)
from memorymarker.question_generator.flows.question_flow import QuestionFlow
from memorymarker.question_generator.pipeline_runner import run_pipelines
from memorymarker.question_generator.qa_responses import QAResponses
from memorymarker.question_generator.steps.qa_extractor import QuestionExtractor
from memorymarker.question_generator.steps.qa_generation import QuestionGenerator
from memorymarker.question_generator.steps.question_wikilinker import QuestionWikilinker
from memorymarker.question_generator.steps.reasoning import Reasoning

if TYPE_CHECKING:
    from memorymarker.question_generator.reasoned_highlight import Highlights

omnivore_cache = Memory(".cache/omnivore")


@dataclass(frozen=True)
class HighlightWithPipeline(PipelineHighlightIdentity):
    highlight: "Highlights"
    pipeline: QuestionFlow

    def identity(self) -> int:
        return self.pipeline_highlight_id(
            self.pipeline.identity, self.highlight.highlighted_text
        )


def _generate_highlight_pipeline_pairs(
    selected_highlights: Iter["Highlights"], pipelines: Sequence[QuestionFlow]
) -> Iter[HighlightWithPipeline]:
    return Iter(
        [
            HighlightWithPipeline(highlight=highlight, pipeline=pipeline)
            for pipeline in pipelines
            for highlight in selected_highlights.to_list()
        ]
    )


@omnivore_cache.cache()  # type: ignore
def _select_highlights_from_omnivore() -> Iter["Highlights"]:
    highlights = (
        Omnivore(
            api_key=os.getenv("OMNIVORE_API_KEY", "No OMNIVORE_API_KEY in environment")
        )
        .get_documents()
        .map(lambda _: _.get_highlights().to_list())
        .flatten()
    )

    return highlights


def chunk_highlights(
    group: tuple[str, Sequence["Highlights"]], chunk_size: int
) -> Sequence["Highlights"]:
    groups: Sequence["Highlights"] = []

    for i in range(0, len(group[1]), 5):
        subset: Sequence["Highlights"] = group[1][i : i + chunk_size]
        combined_text = "\n---\n".join(
            f"> {_.prefix}<HIGHLIGHT>{_.highlighted_text}</HIGHLIGHT>{_.suffix}"
            for _ in subset
        )
        new_highlight = subset[-1]
        new_highlight.highlighted_text = combined_text
        new_highlight.prefix = ""
        new_highlight.suffix = ""
        groups.append(new_highlight)

    return groups


async def main():
    repository = AirtableExampleRepo()
    # content_filter = {
    #     "drenge og mænd ikke har nogen værdi",
    #     "The quality of a model",
    #     "Dependency injection is not effective if",
    #     "The essence of writing code then is to internalize the problem domain",
    #     "stack is a data structure that contains a collection of elements where you can add and delete elements from just one end ",
    #     "A semaphore manages an internal counter",
    # }
    document_titles = {"Singly Linked List"}
    input_highlights = _select_highlights_from_omnivore()
    selected_highlights = input_highlights.filter(
        lambda _: any(title in _.source_document.title for title in document_titles)
    )

    grouped_highlights = (
        selected_highlights.groupby(lambda _: _.source_document.title)
        .map(lambda group: chunk_highlights(group=group, chunk_size=5))
        .flatten()
    )

    old_example_hashes = (
        Iter(repository.get_existing_examples()).map(lambda _: _.__hash__()).to_list()
    )

    base_completer = AnthropicCompleter(
        api_key=os.getenv("ANTHROPIC_API_KEY", None), model="claude-3-opus-20240229"
    )
    # base_completer = OpenAICompleter(
    #     api_key=os.getenv("OPENAI_API_KEY", None), model="gpt-4-turbo-preview"
    # )
    new_highlights = _generate_highlight_pipeline_pairs(
        grouped_highlights,
        [
            QuestionFlow(
                name="chunked_reasoning_with_wikilinks",
                steps=(
                    Reasoning(completer=base_completer),
                    QuestionGenerator(completer=base_completer, n_questions=(1, 5)),
                    QuestionExtractor(
                        completer=OpenAIModelCompleter(
                            api_key=os.getenv("OPENAI_API_KEY", "No OPENAI_API"),
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
            )
        ],
    ).filter(lambda pair: pair.identity() not in old_example_hashes)

    new_responses = await run_pipelines(new_highlights)
    update_repository(new_responses, repository=repository)


if __name__ == "__main__":
    coloredlogs.install(  # type: ignore
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        file_name="tester.log",
    )
    asyncio.run(main())
