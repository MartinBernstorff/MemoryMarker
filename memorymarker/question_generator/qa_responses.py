from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

import pydantic
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight


@dataclass(frozen=True)
class QAPrompt:
    hydrated_highlight: "ReasonedHighlight | None"
    question: str
    answer: str
    title: str

    def to_markdown(self) -> str:
        return f"""{self.question}
{self.answer}
"""


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
    answer: str = Field(
        description="""A brief answer to the question. Must be:
* Concise, one sentence.
* Answerable without the highlight. The question should include any needed context for an expert to accurately answer it. Do not refer to the speaker or the highlight.
* Focused on one point, i.e. never contains "and"
* Specific, i.e. it must be answerable with a brief answer
* Focused on reflection, e.g. comparing options or explaining, rather than defining

Most questions should start with "When X", e.g. "When working on software", to define the context of the question.
"""
    )

    def to_qaprompt(self, reasoned_highlight: "ReasonedHighlight") -> QAPrompt:
        return QAPrompt(
            hydrated_highlight=reasoned_highlight,
            question=self.question,
            answer="",
            title=reasoned_highlight.source_document.title,
        )


class QAResponses(pydantic.BaseModel):
    items: Sequence[QAPromptResponseModel]
