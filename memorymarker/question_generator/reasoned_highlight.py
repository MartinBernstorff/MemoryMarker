from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from memorymarker.document_providers.contextualized_highlight import (
        ContextualizedHighlight,
    )
    from memorymarker.question_generator.qa_responses import QAPrompt


@dataclass(frozen=True)
class ReasonedHighlight:
    pipeline_name: str
    highlight: "ContextualizedHighlight"
    reasoning_prompt: str
    reasoning: str
    question_answer_pairs: Sequence["QAPrompt"]
