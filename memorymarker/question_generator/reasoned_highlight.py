import datetime as dt  # noqa: TCH003
from dataclasses import dataclass
from typing import Sequence

from openai import BaseModel

from memorymarker.question_generator.qa_responses import QAPrompt  # noqa: TCH001


@dataclass(frozen=True)
class SourceDocument:
    title: str
    uri: str


def to_markdown_quote(text: str) -> str:
    lines = [f"> {line}" for line in text.splitlines()]
    return "\n".join(lines)


class ReasonedHighlight(BaseModel):
    source_document: SourceDocument

    updated_at: dt.datetime
    prefix: str
    highlighted_text: str
    suffix: str

    pipeline_name: str

    reasoning_prompt: str
    reasoning: str

    qa_string: str
    question_answer_pairs: Sequence[QAPrompt]

    @property
    def context(self) -> str:
        return f"{self.prefix}{self.highlighted_text}{self.suffix}"

    def to_markdown(self) -> str:
        prefix = to_markdown_quote(self.prefix) if self.prefix else ""
        highlighted = to_markdown_quote(self.highlighted_text)
        suffix = to_markdown_quote(self.suffix.strip()) if self.suffix else ""
        link = f"> \n> [Link]({self.source_document.uri})"

        qa_md = [prompt.to_markdown() for prompt in self.question_answer_pairs]
        return "\n".join((prefix, highlighted, suffix, link, "", *qa_md, ""))
