import gpt2anki.domain.highlights_to_questions as highlights_to_questions
import pytest
from gpt2anki.data_access.highlight_sources.base import HydratedHighlight


# create a pytest fixture for the model
@pytest.fixture(scope="session")
def model() -> highlights_to_questions.ChatOpenAI:
    return highlights_to_questions.initialize_model(model_name="gpt-3.5-turbo")


@pytest.mark.asyncio()
async def test_model_response(model: highlights_to_questions.ChatOpenAI) -> None:
    higlight = HydratedHighlight(
        context="Mitochondria is the powerhouse of the cell",
        highlight="Mitochondria",
        uri="https://en.wikipedia.org/wiki/Mitochondrion",
        title="Mitochondrion - Wikipedia",
    )
    output = await highlights_to_questions.prompt_gpt(model, higlight)
    # check that outpuis a dictionary with keys "answer" and "question"
    assert "answer" in output[0]
    assert "question" in output[0]


@pytest.mark.asyncio()
async def test_multi_response(model: highlights_to_questions.ChatOpenAI) -> None:
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
        ),
    ]
    output = await highlights_to_questions.prompt_gpt(model, highlights)
    assert len(output) == 2
    assert "answer" in output[0]
    assert "question" in output[1]
