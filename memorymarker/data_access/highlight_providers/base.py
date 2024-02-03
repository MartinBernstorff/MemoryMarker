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
    title: str
    highlight: str
    context: str
    uri: str
    updated_at: dt.datetime


class HighlightSource(Protocol):
    def get_highlights_since_date(self, date: dt.datetime) -> tuple[OrphanHighlight]:
        ...


class HighlightManager(Protocol):
    timestamp_file: Path
    source: HighlightSource

    def get_highlights_since_update(
        self, date: dt.datetime
    ) -> Sequence[HydratedHighlight]:
        ...
