import pytest

import src.gpt2anki.magi as magi
from src.gpt2anki.sources.hypothesis import Highlight


# create a pytest fixture for the model
@pytest.fixture(scope="session")
def model() -> magi.ChatOpenAI:
    return magi.initialize_model()


async def test_model_response(model: magi.ChatOpenAI) -> None:
    higlight = Highlight(
        context="Mitochondria is the powerhouse of the cell", highlight="Mitochondria",
    )
    output = await magi.prompt_gpt(model, higlight)
    # check that outpuis a dictionary with keys "answer" and "question"
    assert "answer" in output
    assert "question" in output
