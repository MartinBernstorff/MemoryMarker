from dataclasses import dataclass
from typing import TYPE_CHECKING

from memorymarker.question_generator.expanded_pipeline import Model, PipelineFirstStep

if TYPE_CHECKING:
    from memorymarker.document_providers.contextualized_highlight import (
        ContextualizedHighlight,
    )


@dataclass
class COT(PipelineFirstStep):
    model: Model
    variant: str

    async def __call__(self, highlight: "ContextualizedHighlight") -> str:
        base_prompt = f"""The following is a highlight from a document called "{highlight.source_doc_title}".

Why might a student highlight this sentence? Focus on them wanting to learn something, especially if they can apply it in a situation. Think step by step.

Highlight: {highlight.highlighted_text}
"""
        return base_prompt
