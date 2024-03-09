from dataclasses import dataclass
from typing import TYPE_CHECKING

from memorymarker.question_generator.expanded_pipeline import Model, PipelineFirstStep

if TYPE_CHECKING:
    from memorymarker.document_providers.ContextualizedHighlight import (
        ContextualizedHighlight,
    )


@dataclass
class COT(PipelineFirstStep):
    model: Model
    base_name: str = "5-whys"

    async def __call__(self, highlight: "ContextualizedHighlight") -> str:
        base_prompt = f"""The following is a highlight from a document called "{highlight.source_doc_title}".

Why is this highlight interesting?

Think step by step, with each step being a one-sentece bullet point, written in a concise, to-the point and direct style. Each bullet should be an interesting, different implication from the previous bullet.

Write your response like:
* [Argument...]. Why?
* Because [argument 2]. Why?

Do this 5 or more times.

<highlight>
{highlight.highlighted_text}
</highlight>
"""
        return base_prompt
