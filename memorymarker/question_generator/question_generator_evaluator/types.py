from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from memorymarker.document_providers.contextualized_highlight import (
        ContextualizedHighlight,
    )
    from memorymarker.question_generator.highlight_to_question import (
        HighlightToQuestion,
    )
    from memorymarker.question_generator.qa_prompt import QAPrompt


class SupportsIdentity:
    def identity(self, pipeline_id: str, highlight: str) -> int:
        return f"{pipeline_id}_{highlight}".__hash__()


@dataclass(frozen=True)
class QAPromptWithMetadata:
    prompt: "QAPrompt"
    lineage: Sequence[str]
    pipeline_name: str


@dataclass(frozen=True)
class HighlightWithPipeline(SupportsIdentity):
    highlight: "ContextualizedHighlight"
    pipeline: "HighlightToQuestion"

    def __hash__(self) -> int:
        return self.identity(self.pipeline.name, self.highlight.highlighted_text)
