import datetime as dt

import pytest

import memorymarker.persist_questions.markdown as markdown
from memorymarker.question_generator.question_generator import QAPrompt

from ..document_providers.ContextualizedHighlight import ContextualizedHighlight


class FakeHydratedHighlight(ContextualizedHighlight):
    source_doc_title: str = "The Hitchhiker's Guide to the Galaxy"
    source_doc_uri: str = (
        "https://en.wikipedia.org/wiki/The_Hitchhiker%27s_Guide_to_the_Galaxy"
    )
    source_highlight_uri: str | None = "https://en.wikipedia.org/wiki/The_Hitchhiker%27s_Guide_to_the_Galaxy#meaning_of_life"
    updated_at: dt.datetime = dt.datetime.now()

    prefix: str | None = ""
    highlighted_text: str = "42"
    suffix: str | None = ""


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
