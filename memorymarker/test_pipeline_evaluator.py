import datetime as dt

from iterpy.iter import Iter

from memorymarker.document_providers.ContextualizedHighlight import (
    ContextualizedHighlight,
)
from memorymarker.question_generator.baseline_pipeline import BaselinePipeline
from memorymarker.question_generator.pipeline_evaluator import (
    HighlightPipelinePair,
    PipelineExample,
)


def test_difference():
    existing_highlights = Iter(
        [
            PipelineExample(
                Highlight="test",
                Context="test",
                Question="test",
                Answer="test",
                Pipeline="Baseline-GPT-4",
            )
        ]
    )
    old_hashes = Iter(existing_highlights).map(lambda _: _.__hash__())

    new_highlights = {
        HighlightPipelinePair(
            highlight=ContextualizedHighlight(
                source_doc_title="Test",
                source_doc_uri="https://en.wikipedia.org/wiki/Test",
                highlighted_text="test",
                prefix="",
                suffix="",
                updated_at=dt.datetime.now(),
            ),
            pipeline=BaselinePipeline(
                _name="Baseline-GPT-4", openai_api_key="FAKE", model="gpt-4"
            ),
        )
    }

    difference = Iter(new_highlights).filter(lambda _: _.__hash__() not in old_hashes)
    assert difference.count() == 0
