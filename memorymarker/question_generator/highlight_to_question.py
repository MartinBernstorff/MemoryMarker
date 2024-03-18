from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from iterpy.iter import Iter

    from memorymarker.document_providers.contextualized_highlight import (
        ContextualizedHighlight,
    )
    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight


class HighlightToQuestion(Protocol):
    def __call__(
        self, highlights: "Iter[ContextualizedHighlight]"
    ) -> "Iter[ReasonedHighlight]":
        ...

    @property
    def name(self) -> str:
        ...
