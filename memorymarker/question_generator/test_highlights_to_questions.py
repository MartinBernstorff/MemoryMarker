from datetime import datetime

import pytest

import memorymarker.question_generator.question_generator as h2q
from memorymarker.document_providers.ContextualizedHighlight import (
    ContextualizedHighlight,
)


# create a pytest fixture for the model
@pytest.fixture(scope="session")
def model() -> h2q.ChatOpenAI:
    return h2q.initialize_model(model_name="gpt-3.5-turbo")


@pytest.fixture(scope="module")
def hydrated_highlight() -> ContextualizedHighlight:
    return ContextualizedHighlight(
        prefix="",
        suffix=" is the powerhouse of the cell",
        highlighted_text="Mitochondria",
        source_doc_uri="https://en.wikipedia.org/wiki/Mitochondrion",
        source_doc_title="Mitochondrion - Wikipedia",
        updated_at=datetime.now(),
    )


@pytest.mark.asyncio()
async def test_model_response(
    model: h2q.ChatOpenAI, hydrated_highlight: ContextualizedHighlight
) -> None:
    await h2q.highlights_to_questions(model, [hydrated_highlight])
    # check that outputs an dictionary with keys "answer" and "question"
    # is automatically checked, since highlight_to_questions indexes into it


@pytest.mark.asyncio()
async def test_multi_response(model: h2q.ChatOpenAI) -> None:
    highlights = [
        ContextualizedHighlight(
            prefix="",
            suffix=" is the powerhouse of the cell",
            highlighted_text="Mitochondria",
            source_doc_uri="https://en.wikipedia.org/wiki/Mitochondrion",
            source_doc_title="Mitochondrion - Wikipedia",
            updated_at=datetime.now(),
        ),
        ContextualizedHighlight(
            prefix="The first rule of ",
            suffix=" is that you don't talk about Fight Club",
            highlighted_text="Fight Club",
            source_doc_uri="https://en.wikipedia.org/wiki/Fight_Club",
            source_doc_title="Fight Club - Wikipedia",
            updated_at=datetime.now(),
        ),
    ]
    output = await h2q.highlights_to_questions(model, highlights)
    assert len(output) == 2
