import asyncio
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from iterpy.iter import Iter
from joblib import Memory

from memorymarker.document_providers.omnivore import Omnivore
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
from memorymarker.question_generator.steps.qa_extractor import QuestionExtractionStep
from memorymarker.question_generator.steps.qa_generation import QuestionGenerationStep
from memorymarker.question_generator.steps.reasoning import ReasoningStep

if TYPE_CHECKING:
    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight

omnivore_cache = Memory(".cache/omnivore")


@dataclass(frozen=True)
class HighlightWithPipeline(PipelineHighlightIdentity):
    highlight: "ReasonedHighlight"
    pipeline: "QuestionFlow"

    def __hash__(self) -> int:
        return self.pipeline_highlight_id(
            self.pipeline.name, self.highlight.highlighted_text
        )


def _generate_highlight_pipeline_pairs(
    selected_highlights: Iter["ReasonedHighlight"], pipelines: Sequence["QuestionFlow"]
) -> Iter[HighlightWithPipeline]:
    return Iter(
        [
            HighlightWithPipeline(highlight=highlight, pipeline=pipeline)
            for pipeline in pipelines
            for highlight in selected_highlights.to_list()
        ]
    )


@omnivore_cache.cache()  # type: ignore
def _select_highlights_from_omnivore(
    search_terms: set[str],
) -> Iter["ReasonedHighlight"]:
    highlights = (
        Omnivore(
            api_key=os.getenv("OMNIVORE_API_KEY", "No OMNIVORE_API_KEY in environment")
        )
        .get_documents()
        .map(lambda _: _.get_highlights().to_list())
        .flatten()
    )

    selected_highlights = highlights.filter(
        lambda _: any(term in _.highlighted_text for term in search_terms)
    )

    return selected_highlights


async def main():
    openai_api_key = os.getenv(
        "OPENAI_API_KEY", "No OPENAI_API_KEY environment variable set"
    )
    gpt_4_completer = OpenAICompleter(
        api_key=openai_api_key, model="gpt-4-turbo-preview"
    )

    repository = AirtableExampleRepo()
    selected_highlights = _select_highlights_from_omnivore(
        search_terms={
            "often referred to as fine-tuning",
            "drenge og mænd ikke har nogen værdi",
            "The quality of a model",
            "Dependency injection is not effective if",
            "The essence of writing code then is to internalize the problem domain",
            "stack is a data structure that contains a collection of elements where you can add and delete elements from just one end ",
        }
    )

    old_example_hashes = (
        Iter(repository.get_existing_examples()).map(lambda _: _.__hash__()).to_list()
    )

    new_highlights = _generate_highlight_pipeline_pairs(
        selected_highlights,
        [
            QuestionFlow(
                _name="reasoned_pipeline",
                steps=[
                    ReasoningStep(completer=gpt_4_completer),
                    QuestionGenerationStep(completer=gpt_4_completer),
                    QuestionExtractionStep(
                        completer=OpenAIModelCompleter(
                            api_key=openai_api_key,
                            model="gpt-4-turbo-preview",
                            response_model=QAResponses,  # type: ignore
                        )
                    ),
                ],
            )
        ],
    ).filter(lambda pair: pair.__hash__() not in old_example_hashes)

    new_responses = await run_pipelines(new_highlights)
    update_repository(new_responses, repository=repository)


if __name__ == "__main__":
    asyncio.run(main())
