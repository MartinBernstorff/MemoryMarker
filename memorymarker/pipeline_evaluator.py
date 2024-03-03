import os
import pathlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from pydantic import BaseModel

from memorymarker.document_providers.omnivore import Omnivore
from memorymarker.question_generator.baseline_pipeline import BaselinePipeline

if TYPE_CHECKING:

    from memorymarker.document_providers.ContextualizedHighlight import (
        ContextualizedHighlight,
    )
    from memorymarker.question_generator.highlight_to_question import (
        HighlightToQuestion,
    )
    from memorymarker.question_generator.qa_prompt import QAPrompt

from iterpy.iter import Iter
from pyairtable import Api


class ExampleIdentity:
    def identity(self, pipeline_id: str, highlight: str) -> int:
        return f"{pipeline_id}_{highlight}".__hash__()


@dataclass(frozen=True)
class HighlightPipelinePair(ExampleIdentity):
    highlight: "ContextualizedHighlight"
    pipeline: "HighlightToQuestion"

    def __hash__(self) -> int:
        return self.identity(self.pipeline.name, self.highlight.highlighted_text)


class PipelineExample(BaseModel, ExampleIdentity):
    Highlight: str
    Context: str
    Question: str
    Answer: str
    Pipeline: str

    def __hash__(self) -> int:
        return self.identity(self.Pipeline, self.Highlight)


@dataclass
class AirtableExampleTable:
    base_id: str = "appfcC4kvkTonmm7w"
    table_id: str = "tbldyD9Dk8VddUuRf"

    def __post_init__(self):
        self.client = Api(
            os.getenv("AIRTABLE_PAT", "No AIRTABLE_PAT environment variable set")
        )
        self.table = self.client.base(self.base_id).table(self.table_id)

    def create(self, entity: PipelineExample) -> None:
        self.table.create(entity.model_dump())

    def get_existing_examples(self) -> Sequence[PipelineExample]:
        return [PipelineExample(**row["fields"]) for row in self.table.all()]


@dataclass(frozen=True)
class QAPromptWithPipeline:
    prompt: "QAPrompt"
    pipeline_name: str


def _create_examples(
    pairs: "Iter[HighlightPipelinePair]",
) -> Sequence["QAPromptWithPipeline"]:
    pipelinename2pipeline = {pair.pipeline.name: pair.pipeline for pair in pairs}

    grouped_pairs = pairs.groupby(lambda _: _.pipeline.name)

    examples: Sequence[QAPromptWithPipeline] = []
    for pipeline_name, pair in grouped_pairs:
        print(f"Creating examples for {pipeline_name}")
        pipeline = pipelinename2pipeline[pipeline_name]
        prompts = pipeline(Iter(pair.highlight for pair in pair)).map(
            lambda prompt, pipeline_name=pipeline_name: QAPromptWithPipeline(
                prompt=prompt, pipeline_name=pipeline_name
            )
        )
        examples.extend(prompts.to_list())

    return examples


if __name__ == "__main__":
    search_terms = {
        "gratitude and relatedness",
        "Registry Schema",
        "often referred to as fine-tuning",
        "drenge og mænd ikke har nogen værdi",
        "Underutilized Data Dependencies",
        "The quality of a model",
        "Break down what you want your application",
        "Dependency injection is not effective if",
        "The essence of writing code then is to internalize the problem domain",
    }

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

    pipelines = [
        BaselinePipeline(
            openai_api_key=os.getenv("OPENAI_API_KEY", "No OPENAI_API_KEY set"),
            model="gpt-4",
            name="Baseline-GPT-4",
        ),
        BaselinePipeline(
            openai_api_key=os.getenv("OPENAI_API_KEY", "No OPENAI_API_KEY set"),
            model="gpt-4",
            name="GPT-4-v1-simplified-with-think-step-by-step",
            prompt=(
                pathlib.Path(__file__).parent / "prompts" / "martin_prompt_minimal.txt"
            ).read_text(),
        ),
    ]

    highlight_pipeline_pairs = [
        HighlightPipelinePair(highlight=highlight, pipeline=pipeline)
        for pipeline in pipelines
        for highlight in selected_highlights.to_list()
    ]

    table = AirtableExampleTable()
    existing_examples = table.get_existing_examples()

    new_highlights = Iter(highlight_pipeline_pairs).filter(
        lambda pair: pair.__hash__()
        not in [example.__hash__() for example in existing_examples]
    )

    new_examples = _create_examples(Iter(new_highlights))

    for example in new_examples:
        table.create(
            PipelineExample(
                Highlight=example.prompt.hydrated_highlight.highlighted_text,
                Context=example.prompt.hydrated_highlight.context,
                Question=example.prompt.question,
                Answer=example.prompt.answer,
                Pipeline=example.pipeline_name,
            )
        )
