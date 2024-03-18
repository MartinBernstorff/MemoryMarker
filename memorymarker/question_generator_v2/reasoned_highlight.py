from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from memorymarker.document_providers.contextualized_highlight import (
        ContextualizedHighlight,
    )
    from memorymarker.question_generator.qa_prompt import QAPromptResponseModel


@dataclass(frozen=True)
class ReasonedHighlight:
    highlight: "ContextualizedHighlight"
    reasoning: str | None
    question_answer_pairs: Sequence["QAPromptResponseModel"]
    pipeline_name: str
