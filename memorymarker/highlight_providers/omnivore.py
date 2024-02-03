import os
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from iterpy._iter import Iter
from omnivoreql import OmnivoreQL
from pydantic import BaseModel

from .base import HighlightSource, HydratedHighlight


class Article(BaseModel):
    title: str
    uri: str
    slug: str
    highlights: Sequence[Mapping[str, Any]]

    def _parse_highlight(self, highlight: Mapping[str, str]) -> HydratedHighlight:
        return HydratedHighlight(
            source_doc_title=self.title,
            source_doc_uri=self.uri,
            highlighted_text=highlight["quote"],
            context=f"{highlight['prefix']} {highlight['quote']} {highlight['suffix']}",
            updated_at=highlight["updatedAt"],  # type: ignore
            source_highlight_uri=f"https://omnivore.app/me/{self.slug}#{highlight["id"]}",
        )

    def get_highlights(self) -> Sequence[HydratedHighlight]:
        parsed_highlights = []

        for highlight in self.highlights:
            parsed_highlights.append(self._parse_highlight(highlight))

        return parsed_highlights


@dataclass
class Omnivore(HighlightSource):
    def __post_init__(self):
        omnivore_api_key = os.getenv("OMNIVORE_API_KEY")
        if not omnivore_api_key:
            raise ValueError("OMNIVORE_API_KEY environment variable not set")
        self.client = OmnivoreQL(omnivore_api_key)

    def _parse_article(self, article: Mapping[str, str]) -> Sequence[HydratedHighlight]:
        return Article(
            title=article["title"],
            uri=article["url"],
            highlights=article["highlights"],  # type: ignore
            slug=article["slug"],
        ).get_highlights()

    def get_highlights(self) -> Iter[HydratedHighlight]:
        highlights = (
            Iter(self.client.get_articles(limit=1000)["search"]["edges"])
            .map(lambda a: a["node"])
            .map(self._parse_article)
            .flatten()
        )
        return highlights
