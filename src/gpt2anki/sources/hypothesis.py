import datetime as dt

from gpt2anki.sources.base import Highlight, HighlightSource


class HypothesisHighlight(HighlightSource):
    def __init__(self, api_key: str):
        self.api_key: str = api_key

    def get_highlights_since_date(self, date: dt.datetime) -> tuple[Highlight]:
        raise NotImplementedError
