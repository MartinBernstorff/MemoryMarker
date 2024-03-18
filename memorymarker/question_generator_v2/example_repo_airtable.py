import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from pyairtable import Api
from pydantic import BaseModel

from memorymarker.question_generator.question_generator_evaluator.types import (
    SupportsIdentity,
)

if TYPE_CHECKING:
    from iterpy.iter import Iter

    from memorymarker.question_generator_v2.reasoned_highlight import ReasonedHighlight


class QATableRow(BaseModel, SupportsIdentity):
    Highlight: str
    Context: str
    Question: str
    Answer: str
    Pipeline: str

    def __hash__(self) -> int:
        return self.identity(self.Pipeline, self.Highlight)


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
        for value in rows:
            for possibly_empty_fields in ["Pipeline"]:
                if not value[possibly_empty_fields]:
                    value[possibly_empty_fields] = ""

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
                )
            )
