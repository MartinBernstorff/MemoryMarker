from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    import datetime as dt

    from memorymarker.question_generator.qa_responses import QAPrompt


@dataclass(frozen=True)
class SourceDocument:
    title: str
    uri: str


@dataclass(frozen=True)
class ReasonedHighlight:
    source_document: SourceDocument

    updated_at: "dt.datetime"
    prefix: str
    highlighted_text: str
    suffix: str

    pipeline_name: str

    reasoning_prompt: str
    reasoning: str

    qa_string: str
    question_answer_pairs: Sequence["QAPrompt"]

    @property
    def context(self) -> str:
        return f"{self.prefix}{self.highlighted_text}{self.suffix}"
