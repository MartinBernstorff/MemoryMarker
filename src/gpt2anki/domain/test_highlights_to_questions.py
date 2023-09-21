import gpt2anki.domain.highlights_to_questions as highlights_to_questions
import pytest
from gpt2anki.data_access.highlight_sources.base import HydratedHighlight


# create a pytest fixture for the model
@pytest.fixture(scope="session")
def model() -> highlights_to_questions.ChatOpenAI:
    return highlights_to_questions.initialize_model(model_name="gpt-3.5-turbo")


@pytest.fixture(scope="module")
def hydrated_highlight() -> HydratedHighlight:
    return HydratedHighlight(
        context="Mitochondria is the powerhouse of the cell",
        highlight="Mitochondria",
        uri="https://en.wikipedia.org/wiki/Mitochondrion",
        title="Mitochondrion - Wikipedia",
    )


@pytest.mark.asyncio()
async def test_model_response(
    model: highlights_to_questions.ChatOpenAI,
    hydrated_highlight: HydratedHighlight,
) -> None:
    await highlights_to_questions.highlights_to_questions(
        model,
        [hydrated_highlight],
    )
    # check that outputs an dictionary with keys "answer" and "question"
    # is automatically checked, since highlight_to_questions indexes into it


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
    output = await highlights_to_questions.highlights_to_questions(model, highlights)
    assert len(output) == 2
