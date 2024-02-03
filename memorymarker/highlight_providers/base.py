import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

from pydantic import BaseModel


@dataclass(frozen=True)
class OrphanHighlight:
    highlight: str
    uri: str
    title: str


class HydratedHighlight(BaseModel):
    source_doc_title: str
    source_doc_uri: str
    highlighted_text: str
    context: str
    source_highlight_uri: str | None = None
    updated_at: dt.datetime


class HighlightSource(Protocol):
    def get_highlights(self) -> tuple[OrphanHighlight]:
        ...


class HighlightManager(Protocol):
    timestamp_file: Path
    source: HighlightSource

    def get_highlights_since_update(
        self, date: dt.datetime
    ) -> Sequence[HydratedHighlight]:
        ...
