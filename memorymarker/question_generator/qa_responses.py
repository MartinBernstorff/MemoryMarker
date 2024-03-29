from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

import pydantic
from pydantic import BaseModel, Field

from memorymarker.document_providers.contextualized_highlight import (
    ContextualizedHighlight,
)

if TYPE_CHECKING:
    from memorymarker.document_providers.contextualized_highlight import (
        ContextualizedHighlight,
    )


@dataclass(frozen=True)
class QAPrompt:
    hydrated_highlight: "ContextualizedHighlight"
    question: str
    answer: str
    title: str


class QAPromptResponseModel(BaseModel):
    question: str = Field(
        description="""A question inspiring reflection. Must be:
* Concise, one sentence.
* Answerable without the highlight. The question should include any needed context for an expert to accurately answer it. Do not refer to the speaker or the highlight.
* Focused on one point, i.e. never contains "and"
* Specific, i.e. it must be answerable with a brief answer
* Focused on reflection, e.g. comparing options or explaining, rather than defining

Most questions should start with "When X", e.g. "When working on software", to define the context of the question.
"""
    )

    def to_qaprompt(self, hydrated_highlight: "ContextualizedHighlight") -> QAPrompt:
        return QAPrompt(
            hydrated_highlight=hydrated_highlight,
            question=self.question,
            answer="",
            title=hydrated_highlight.source_doc_title,
        )


class QAResponses(pydantic.BaseModel):
    items: Sequence[QAPromptResponseModel]
