import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from pyairtable import Api
from pydantic import BaseModel

from memorymarker.question_generator.question_generator_evaluator.types import (
    QAPromptWithMetadata,
    SupportsIdentity,
)

if TYPE_CHECKING:
    from iterpy.iter import Iter


class QATableRow(BaseModel, SupportsIdentity):
    Highlight: str
    Context: str
    Question: str
    Answer: str
    Pipeline: str
    Lineage: str

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
        return [QATableRow(**row["fields"]) for row in self.table.all()]


def update_repository(
    new_responses: "Iter[QAPromptWithMetadata]", repository: AirtableExampleRepo
):
    for example in new_responses:
        print(f"Updating {example.prompt}")
        repository.create(
            QATableRow(
                Highlight=example.prompt.hydrated_highlight.highlighted_text,
                Context=example.prompt.hydrated_highlight.context,
                Question=example.prompt.question,
                Answer=example.prompt.answer,
                Pipeline=example.pipeline_name,
                Lineage="\n--- \n\n".join(example.lineage),
            )
        )
