from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

import pydantic
from pydantic import BaseModel

if TYPE_CHECKING:
    from memorymarker.question_generator.reasoned_highlight import Highlights


@dataclass
class QAPrompt:
    hydrated_highlight: "Highlights | None"
    question: str
    answer: str
    title: str

    def to_markdown(self) -> str:
        return f"""{self.question}
{self.answer}
"""


class QAPromptResponseModel(BaseModel):
    question: str
    answer: str

    def to_qaprompt(self, reasoned_highlight: "Highlights") -> QAPrompt:
        return QAPrompt(
            hydrated_highlight=reasoned_highlight,
            question=self.question,
            answer=self.answer,
            title=reasoned_highlight.source_document.title,
        )


class QuestionResponseModel(BaseModel):
    question: str


class QAResponses(pydantic.BaseModel):
    items: Sequence[QAPromptResponseModel]
