import datetime as dt
from typing import Sequence

import pytest

import memorymarker.persist_questions.markdown as markdown
from memorymarker.question_generator.qa_responses import QAPrompt
from memorymarker.question_generator.reasoned_highlight import (
    ReasonedHighlight,
    SourceDocument,
)


class FakeHydratedHighlight(ReasonedHighlight):
    source_document: SourceDocument = SourceDocument(
        title="The Hitchhiker's Guide to the Galaxy",
        uri="https://en.wikipedia.org/wiki/The_Hitchhiker%27s_Guide_to_the_Galaxy#meaning_of_life",
    )

    updated_at: dt.datetime = dt.datetime.now()

    prefix: str = ""
    highlighted_text: str = "42"
    suffix: str = ""

    question_answer_pairs: Sequence[QAPrompt] = []

    pipeline_name: str = "fake_pipeline"

    reasoning_prompt: str = ""
    reasoning: str = ""

    qa_string: str = ""


@pytest.fixture(scope="module")
def question() -> QAPrompt:
    return QAPrompt(
        question="What is the meaning of life?",
        answer="42",
        title="The Hitchhiker's Guide to the Galaxy",
        hydrated_highlight=FakeHydratedHighlight(),
    )


def test_single_q_to_markdown(question: QAPrompt, snapshot) -> None:  # noqa: ANN001
    input_md = markdown.q_to_markdown(question)
    assert snapshot == input_md


@pytest.mark.parametrize(
    ("input_filename", "expect_filename"),
    [
        (
            "Wikipedia · Powerhouse of the cell - Testing",
            "Wikipedia, Powerhouse of the cell, Testing",
        )
    ],
)
def test_clean_filename(input_filename: str, expect_filename: str) -> None:
    assert markdown._clean_filename(input_filename) == expect_filename
