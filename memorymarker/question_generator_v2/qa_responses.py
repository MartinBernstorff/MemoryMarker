from typing import TYPE_CHECKING, Sequence

from pydantic import BaseModel

from memorymarker.question_generator.qa_prompt import QAPrompt

if TYPE_CHECKING:
    from memorymarker.document_providers.contextualized_highlight import (
        ContextualizedHighlight,
    )


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
    items: Sequence[QAPromptResponseModel]
