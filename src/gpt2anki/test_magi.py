import pytest

import gpt2anki.magi as magi
from gpt2anki.sources.hypothesis import Highlight


# create a pytest fixture for the model
@pytest.fixture(scope="session")
def model() -> magi.ChatOpenAI:
    return magi.initialize_model(model_name="gpt-3.5-turbo")


@pytest.mark.asyncio()
async def test_model_response(model: magi.ChatOpenAI) -> None:
    higlight = Highlight(
        context="Mitochondria is the powerhouse of the cell",
        highlight="Mitochondria",
    )
    output = await magi.prompt_gpt(model, higlight)
    # check that outpuis a dictionary with keys "answer" and "question"
    assert "answer" in output
    assert "question" in output
    assert len(output) == 2
