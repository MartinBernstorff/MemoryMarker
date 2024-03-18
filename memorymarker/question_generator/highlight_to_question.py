from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from iterpy.iter import Iter

    from memorymarker.document_providers.ContextualizedHighlight import (
        ContextualizedHighlight,
    )
    from memorymarker.question_generator.expanded_pipeline import PromptWithLineage


class HighlightToQuestion(Protocol):
    def __call__(
        self, highlights: "Iter[ContextualizedHighlight]"
    ) -> "Iter[PromptWithLineage]":
        ...

    @property
    def name(self) -> str:
        ...
