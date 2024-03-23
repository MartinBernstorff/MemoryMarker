import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from iterpy.iter import Iter

from memorymarker.document_providers.contextualized_highlight import (
    ContextualizedHighlight,
)
from memorymarker.document_providers.omnivore import Omnivore
from memorymarker.question_generator.baseline_pipeline import BaselinePipeline
from memorymarker.question_generator.example_repo_airtable import (
    AirtableExampleRepo,
    PipelineHighlightIdentity,
    update_repository,
)
from memorymarker.question_generator.highlight_to_question import HighlightToQuestion
from memorymarker.question_generator.pipeline_runner import run_pipelines
from memorymarker.question_generator.reasoned_pipeline import ReasonedPipeline

if TYPE_CHECKING:
    from memorymarker.document_providers.contextualized_highlight import (
        ContextualizedHighlight,
    )
    from memorymarker.question_generator.highlight_to_question import (
        HighlightToQuestion,
    )


@dataclass(frozen=True)
class HighlightWithPipeline(PipelineHighlightIdentity):
    highlight: "ContextualizedHighlight"
    pipeline: "HighlightToQuestion"

    def __hash__(self) -> int:
        return self.pipeline_highlight_id(
            self.pipeline.name, self.highlight.highlighted_text
        )


def _generate_highlight_pipeline_pairs(
    selected_highlights: Iter["ContextualizedHighlight"],
    pipelines: Sequence["HighlightToQuestion"],
) -> Iter[HighlightWithPipeline]:
    return Iter(
        [
            HighlightWithPipeline(highlight=highlight, pipeline=pipeline)
            for pipeline in pipelines
            for highlight in selected_highlights.to_list()
        ]
    )


def _select_highlights_from_omnivore(
    search_terms: set[str],
) -> Iter["ContextualizedHighlight"]:
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


if __name__ == "__main__":
    repository = AirtableExampleRepo()
    selected_highlights = _select_highlights_from_omnivore(
        search_terms={
            # "gratitude and relatedness",
            # "Registry Schema",
            # "often referred to as fine-tuning",
            # "drenge og mænd ikke har nogen værdi",
            # "Underutilized Data Dependencies",
            # "The quality of a model",
            # "Break down what you want your application",
            # "Dependency injection is not effective if",
            "The essence of writing code then is to internalize the problem domain"
        }
    )

    old_example_hashes = (
        Iter(repository.get_existing_examples()).map(lambda _: _.__hash__()).to_list()
    )

    new_highlights = _generate_highlight_pipeline_pairs(
        selected_highlights,
        [
            ReasonedPipeline(
                _name="reasoned_pipeline",
                openai_api_key=os.getenv(
                    "OPENAI_API_KEY", "No OPENAI_API_KEY environment variable set"
                ),
                model="gpt-4-turbo-preview",
            ),
            BaselinePipeline(
                openai_api_key=os.getenv(
                    "OPENAI_API_KEY", "No OPENAI_API_KEY environment variable set"
                ),
                model="gpt-4-turbo-preview",
                _name="gpt-4-basic",
            ),
        ],
    ).filter(lambda pair: pair.__hash__() not in old_example_hashes)

    new_responses = Iter(run_pipelines(new_highlights)).flatten()
    update_repository(new_responses, repository=repository)
