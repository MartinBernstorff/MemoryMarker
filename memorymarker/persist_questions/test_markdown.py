import datetime as dt

import pytest

import memorymarker.persist_questions.markdown as markdown
from memorymarker.question_generator.qa_responses import QAPrompt
from memorymarker.question_generator.reasoned_highlight import (
    ReasonedHighlight,
    SourceDocument,
)


class FakeHydratedHighlight(ReasonedHighlight):
    source_document = SourceDocument(
        title="The Hitchhiker's Guide to the Galaxy",
        uri="https://en.wikipedia.org/wiki/The_Hitchhiker%27s_Guide_to_the_Galaxy",
    )

    updated_at: dt.datetime = dt.datetime.now()

    prefix: str = ""
    highlighted_text: str = "42"
    suffix: str = ""

    question_answer_pairs = ()


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


def test_clean_filename():
    filename = "Wikipedia · Powerhouse of the cell - Testing"
    result = markdown.clean_filename(filename)
    assert result == "Wikipedia___Powerhouse_of_the_cell___Testing"
