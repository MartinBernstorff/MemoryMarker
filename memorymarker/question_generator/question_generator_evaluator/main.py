import os
from typing import TYPE_CHECKING, Sequence

from iterpy.iter import Iter

from memorymarker.document_providers.omnivore import Omnivore
from memorymarker.question_generator.expanded_pipeline import GPT4, ExpandedPipeline
from memorymarker.question_generator.question_generator_evaluator.example_repo_airtable import (
    AirtableExampleRepo,
    update_repository,
)
from memorymarker.question_generator.question_generator_evaluator.pipeline_runner import (
    run_pipelines,
)
from memorymarker.question_generator.question_generator_evaluator.types import (
    HighlightWithPipeline,
)
from memorymarker.question_generator.steps.final_steps import QuestionExtractor
from memorymarker.question_generator.steps.first_steps import COT
from memorymarker.question_generator.steps.middle_steps import StudentReflection

if TYPE_CHECKING:
    from memorymarker.document_providers.ContextualizedHighlight import (
        ContextualizedHighlight,
    )
    from memorymarker.question_generator.highlight_to_question import (
        HighlightToQuestion,
    )


def _get_highlights(search_terms: set[str]) -> Iter["ContextualizedHighlight"]:
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


def _generate_highlight_pipeline_pairs(
    selected_highlights: Iter["ContextualizedHighlight"],
    pipelines: Sequence["HighlightToQuestion"],
) -> Iter[HighlightWithPipeline]:
    highlight_pipeline_pairs = [
        HighlightWithPipeline(highlight=highlight, pipeline=pipeline)
        for pipeline in pipelines
        for highlight in selected_highlights.to_list()
    ]
    old_example_hashes = (
        Iter(AirtableExampleRepo().get_existing_examples())
        .map(lambda _: _.__hash__())
        .to_list()
    )
    new_highlights = Iter(highlight_pipeline_pairs).filter(
        lambda pair: pair.__hash__() not in old_example_hashes
    )

    return new_highlights


if __name__ == "__main__":
    selected_highlights = _get_highlights(
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

    pipelines = [
        ExpandedPipeline(
            first_step=COT(
                model=GPT4(os.getenv("OPENAI_API_KEY", "No OPENAI_API_KEY set")),
                variant="cot-application",
            ),
            steps=[
                StudentReflection(
                    model=GPT4(os.getenv("OPENAI_API_KEY", "No OPENAI_API_KEY set")),
                    variant="reflection-and-elaboration",
                )
            ],
            final_step=QuestionExtractor(
                openai_api_key=os.getenv("OPENAI_API_KEY", "No OPENAI key specified")
            ),
        )
    ]

    new_highlights = _generate_highlight_pipeline_pairs(selected_highlights, pipelines)
    new_responses = Iter(run_pipelines(new_highlights)).flatten()
    update_repository(new_responses, repository=AirtableExampleRepo())
