from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from memorymarker.document_providers.contextualized_highlight import (
        ContextualizedHighlight,
    )
    from memorymarker.question_generator.qa_prompt import QAPrompt


@dataclass(frozen=True)
class ReasonedHighlight:
    highlight: "ContextualizedHighlight"
    reasoning: str | None
    question_answer_pairs: Sequence["QAPrompt"]
    pipeline_name: str
