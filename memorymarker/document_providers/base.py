from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, Sequence

if TYPE_CHECKING:
    import datetime as dt
    from pathlib import Path

    from iterpy.iter import Iter

    from memorymarker.document_providers.ContextualizedHighlight import (
        ContextualizedHighlight,
    )

    from .Document import Document


@dataclass(frozen=True)
class OrphanHighlight:
    highlight: str
    uri: str
    title: str


class DocumentProvider(Protocol):
    def get_documents(self) -> "Iter[Document]":
        ...


class HighlightManager(Protocol):
    timestamp_file: "Path"
    source: DocumentProvider

    def get_highlights_since_update(
        self, date: "dt.datetime"
    ) -> Sequence["ContextualizedHighlight"]:
        ...
