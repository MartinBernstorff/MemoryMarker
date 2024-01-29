from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Sequence

import pytest
from iterpy._iter import Iter

import memorymarker.domain.highlights_to_questions as h2q
from memorymarker.data_access.highlight_sources.base import HydratedHighlight


# create a pytest fixture for the model
@pytest.fixture(scope="session")
def model() -> h2q.ChatOpenAI:
    return h2q.initialize_model(model_name="gpt-3.5-turbo")


@pytest.fixture(scope="module")
def hydrated_highlight() -> HydratedHighlight:
    return HydratedHighlight(
        context="Mitochondria is the powerhouse of the cell",
        highlight="Mitochondria",
        uri="https://en.wikipedia.org/wiki/Mitochondrion",
        title="Mitochondrion - Wikipedia",
        updated_at=datetime.now(),
    )


@pytest.mark.asyncio()
async def test_model_response(
    model: h2q.ChatOpenAI,
    hydrated_highlight: HydratedHighlight,
) -> None:
    await h2q.highlights_to_questions(
        model,
        [hydrated_highlight],
    )
    # check that outputs an dictionary with keys "answer" and "question"
    # is automatically checked, since highlight_to_questions indexes into it


@pytest.mark.asyncio()
async def test_multi_response(model: h2q.ChatOpenAI) -> None:
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
    output = await h2q.highlights_to_questions(model, highlights)
    assert len(output) == 2
