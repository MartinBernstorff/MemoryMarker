from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from iterpy.iter import Iter
from omnivoreql import OmnivoreQL
from pydantic import BaseModel

from memorymarker.question_generator.reasoned_highlight import (
    Highlights,
    SourceDocument,
)

from .base import DocumentProvider


def _empty_string_if_none(value: str | None) -> str:
    return value or ""


class OmnivoreDocument(BaseModel):
    title: str
    uri: str
    slug: str
    highlights: Sequence[Mapping[str, Any]]

    def _parse_highlight(self, highlight: Mapping[str, str]) -> Highlights | None:
        if "quote" not in highlight or highlight["quote"] is None:  # type: ignore
            return None

        return Highlights(
            source_document=SourceDocument(
                title=self.title,
                uri=f"https://omnivore.app/me/{self.slug}#{highlight["id"]}",
            ),
            pipeline_name="",
            reasoning_prompt="",
            reasoning="",
            qa_string="",
            question_answer_pairs=[],
            highlighted_text=highlight["quote"],
            prefix=_empty_string_if_none(highlight["prefix"]),
            suffix=_empty_string_if_none(highlight["suffix"]),
            updated_at=highlight["updatedAt"],  # type: ignore # Will be recast on init.
        )

    def get_highlights(self) -> Iter[Highlights]:
        highlights = Iter(self.highlights).map(self._parse_highlight)
        return highlights.filter(lambda _: _ is not None)  # type: ignore


@dataclass
class Omnivore(DocumentProvider):
    api_key: str

    def __post_init__(self):
        self.client = OmnivoreQL(self.api_key)

    def _parse_doc(self, document: Mapping[str, str]) -> OmnivoreDocument:
        return OmnivoreDocument(
            title=document["title"],
            uri=document["url"],
            highlights=document["highlights"],  # type: ignore
            slug=document["slug"],
        )

    def get_documents(self) -> Iter[OmnivoreDocument]:
        documents = (
            Iter(self.client.get_articles(limit=1000)["search"]["edges"])
            .map(lambda a: a["node"])
            .map(self._parse_doc)
            .flatten()
        )
        return documents
