from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

import attrs
from attrs import define
from openai import BaseModel

if TYPE_CHECKING:
    import datetime as dt

    from memorymarker.question_generator.qa_responses import QAPrompt


@dataclass(frozen=True)
class SourceDocument:
    title: str
    uri: str


class ReasonedHighlight(BaseModel):
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


@define
class C:
    test: str


if __name__ == "__main__":
    test_class = C(test="Testing")
    two = attrs.evolve(test_class, test2="Testing2")
