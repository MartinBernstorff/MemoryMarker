import datetime as dt
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Highlight:
    context: str
    highlight: str


class HighlightSource(ABC):
    @abstractmethod
    def get_highlights_since_date(self, date: dt.datetime) -> Tuple[Highlight]:
        raise NotImplementedError
