from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from pydantic import BaseModel

if TYPE_CHECKING:
    from memorymarker.document_providers.ContextualizedHighlight import (
        ContextualizedHighlight,
    )


@dataclass(frozen=True)
class QAPrompt:
    hydrated_highlight: "ContextualizedHighlight"
    question: str
    answer: str
    title: str


class QAPromptResponseModel(BaseModel):
    question: str
    answer: str

    def to_qaprompt(self, hydrated_highlight: "ContextualizedHighlight") -> QAPrompt:
        return QAPrompt(
            hydrated_highlight=hydrated_highlight,
            question=self.question,
            answer="",
            title=hydrated_highlight.source_doc_title,
        )


class QAResponses(BaseModel):
    responses: Sequence[QAPromptResponseModel]
