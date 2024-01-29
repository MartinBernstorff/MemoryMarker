import datetime as dt
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class OrphanHighlight:
    highlight: str
    uri: str
    title: str


@dataclass(frozen=True)
class HydratedHighlight:
    title: str
    highlight: str
    context: str
    uri: str


class HighlightSource(ABC):
    @abstractmethod
    def get_highlights_since_date(self, date: dt.datetime) -> tuple[OrphanHighlight]:
        raise NotImplementedError
