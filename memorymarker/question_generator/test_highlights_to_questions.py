import os
from datetime import datetime
from typing import TYPE_CHECKING

import pytest
from iterpy.iter import Iter

import memorymarker.question_generator.baseline_pipeline as h2q
from memorymarker.document_providers.contextualized_highlight import (
    ContextualizedHighlight,
)

if TYPE_CHECKING:
    from memorymarker.question_generator.highlight_to_question import (
        HighlightToQuestion,
    )


@pytest.mark.parametrize(
    ("pipeline"),
    [
        h2q.BaselinePipeline(
            openai_api_key=os.getenv("OPENAI_API_KEY", "FAILED_TO_FIND_PROMPT_IN_ENV"),
            model="gpt-3.5-turbo",
            _name="gpt-3.5-testing",
        )
    ],
)
def test_multi_response(pipeline: "HighlightToQuestion") -> None:
    highlights = Iter(
        [
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
    )
    output = pipeline(highlights)
    assert output.count() == 2
