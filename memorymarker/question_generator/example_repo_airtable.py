import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from pyairtable import Api
from pydantic import BaseModel

if TYPE_CHECKING:
    from iterpy.iter import Iter

    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight


class PipelineHighlightIdentity:
    def pipeline_highlight_id(self, pipeline_id: str, highlight: str) -> int:
        return f"{pipeline_id}_{highlight}".__hash__()


class QATableRow(BaseModel, PipelineHighlightIdentity):
    Highlight: str
    Context: str
    Question: str
    Answer: str
    ReasoningPrompt: str
    Reasoning: str
    Pipeline: str

    def __hash__(self) -> int:
        return self.pipeline_highlight_id(self.Pipeline, self.Highlight)


@dataclass
class AirtableExampleRepo:
    base_id: str = "appfcC4kvkTonmm7w"
    table_id: str = "tbldyD9Dk8VddUuRf"

    def __post_init__(self):
        self.client = Api(
            os.getenv("AIRTABLE_PAT", "No AIRTABLE_PAT environment variable set")
        )
        self.table = self.client.base(self.base_id).table(self.table_id)

    def create(self, entity: QATableRow) -> None:
        self.table.create(entity.model_dump())

    def get_existing_examples(self) -> Sequence[QATableRow]:
        rows = self.table.all()
        for row in rows:
            for possibly_missing_field in [
                "Pipeline",
                "ReasoningPrompt",
                "Reasoning",
                "Answer",
            ]:
                try:
                    print(row[possibly_missing_field])  # type: ignore
                except KeyError:
                    row["fields"][possibly_missing_field] = ""

        return [QATableRow(**row["fields"]) for row in rows]


def update_repository(
    new_responses: "Iter[ReasonedHighlight]", repository: AirtableExampleRepo
):
    for example in new_responses:
        for qa_pair in example.question_answer_pairs:
            repository.create(
                QATableRow(
                    Highlight=example.highlight.highlighted_text,
                    Context=example.highlight.context,
                    Question=qa_pair.question,
                    Answer=qa_pair.answer,
                    Pipeline=example.pipeline_name,
                    Reasoning=example.reasoning,
                    ReasoningPrompt=example.reasoning_prompt,
                )
            )
