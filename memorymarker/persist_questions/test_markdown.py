import pytest

import memorymarker.persist_questions.markdown as markdown
from memorymarker.question_generator.question_generator import QAPrompt


@pytest.fixture(scope="module")
def question() -> QAPrompt:
    return QAPrompt(
        question="What is the meaning of life?",
        answer="42",
        title="The Hitchhiker's Guide to the Galaxy",
    )


def test_single_q_to_markdown(question: QAPrompt) -> None:
    input_md = markdown.q_to_markdown(question)
    expected = "Q. What is the meaning of life?\nA. 42\n\n"
    assert input_md == expected


def test_clean_filename():
    filename = "Wikipedia · Powerhouse of the cell - Testing"
    result = markdown.clean_filename(filename)
    assert result == "Wikipedia___Powerhouse_of_the_cell___Testing"
