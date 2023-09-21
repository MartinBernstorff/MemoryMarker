import gpt2anki.markdown as markdown
import pytest


@pytest.fixture(scope="module")
def question() -> dict[str, str]:
    return {
        "question": "What is the meaning of life?",
        "answer": "42",
    }


def test_single_q_to_markdown(question: dict[str, str]) -> None:
    input_md = markdown.q_to_markdown(question)
    expected = "Q: What is the meaning of life?\nA: 42\n\n"
    assert input_md == expected
