import datetime as dt
from typing import Sequence

import pytest

import memorymarker.persister.markdown as markdown
from memorymarker.question_generator.qa_responses import QAPrompt
from memorymarker.question_generator.reasoned_highlight import (
    Highlights,
    SourceDocument,
)


class FakeHydratedHighlight(Highlights):
    source_document: SourceDocument = SourceDocument(
        title="The Hitchhiker's Guide to the Galaxy",
        uri="https://en.wikipedia.org/wiki/The_Hitchhiker%27s_Guide_to_the_Galaxy#meaning_of_life",
    )

    updated_at: dt.datetime = dt.datetime.now()

    prefix: str = "What is the answer to the ultimate question of life, the universe, and everything? "
    highlighted_text: str = "42."
    suffix: str = " Of course, this was a very simple question for the supercomputer Deep Thought, the second greatest computer of all time, the greatest being the Earth itself.\n\nDeep Thought was created to answer the ultimate question of life, the universe, and everything. It took Deep Thought 7½ million years to compute and check the answer, which turns out to be 42."

    question_answer_pairs: Sequence[QAPrompt] = [
        QAPrompt(
            question="What is the meaning of life?",
            answer="42",
            hydrated_highlight=None,
            title="The Hitchhiker's Guide to the Galaxy",
        )
    ]

    pipeline_name: str = "fake_pipeline"

    reasoning_prompt: str = ""
    reasoning: str = ""

    qa_string: str = ""


@pytest.mark.parametrize(("highlight"), [FakeHydratedHighlight()])
def test_highlight_to_md(highlight: FakeHydratedHighlight, snapshot) -> None:  # noqa: ANN001
    input_md = highlight.to_markdown()
    assert snapshot == input_md


@pytest.fixture(scope="module")
def question() -> QAPrompt:
    return QAPrompt(
        question="What is the meaning of life?",
        answer="42",
        title="The Hitchhiker's Guide to the Galaxy",
        hydrated_highlight=FakeHydratedHighlight(),
    )


def test_single_q_to_markdown(question: QAPrompt, snapshot) -> None:  # noqa: ANN001
    input_md = question.to_markdown()
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
    assert markdown.clean_filename(input_filename) == expect_filename
