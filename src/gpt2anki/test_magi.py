import pytest

import gpt2anki.magi as magi
from gpt2anki.sources.base import HydratedHighlight


# create a pytest fixture for the model
@pytest.fixture(scope="session")
def model() -> magi.ChatOpenAI:
    return magi.initialize_model(model_name="gpt-3.5-turbo")


@pytest.mark.asyncio()
async def test_model_response(model: magi.ChatOpenAI) -> None:
    higlight = HydratedHighlight(
        context="Mitochondria is the powerhouse of the cell",
        highlight="Mitochondria",
        uri="https://en.wikipedia.org/wiki/Mitochondrion",
        title="Mitochondrion - Wikipedia",
    )
    output = await magi.prompt_gpt(model, higlight)
    # check that outpuis a dictionary with keys "answer" and "question"
    assert "answer" in output[0]
    assert "question" in output[0]

@pytest.mark.asyncio()
async def test_multi_response(model: magi.ChatOpenAI) -> None:
    highlights = [
     HydratedHighlight(
        context="Mitochondria is the powerhouse of the cell",
        highlight="Mitochondria",
        uri="https://en.wikipedia.org/wiki/Mitochondrion",
        title="Mitochondrion - Wikipedia",
    ),
    HydratedHighlight(
        context="The first rule of Fight Club is that you don't talk about Fight Club",
        highlight="Fight Club",
        uri="https://en.wikipedia.org/wiki/Fight_Club",
        title="Fight Club - Wikipedia",
    )
    ]
    output = await magi.prompt_gpt(model, highlights)
    assert len(output) == 2
    assert "answer" in output[0]
    assert "question" in output[1]
    