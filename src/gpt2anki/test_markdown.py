import pytest

import gpt2anki.markdown as markdown
@pytest.fixture(scope="module")
def question() -> dict[str, str]:
    return {
        "question": "What is the meaning of life?",
        "answer": "42",
    }

def test_single_q_to_markdown(question) -> None:
    input_md = markdown.q_to_markdown(question)
    expected = "Q: What is the meaning of life?\nA: 42\n\n"
    assert input_md == expected