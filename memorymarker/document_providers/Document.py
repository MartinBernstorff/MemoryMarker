from typing import Any, Mapping, Sequence

from iterpy.iter import Iter
from pydantic import BaseModel

from .contextualized_highlight import ContextualizedHighlight


class Document(BaseModel):
    title: str
    uri: str
    slug: str
    highlights: Sequence[Mapping[str, Any]]

    def _parse_highlight(
        self, highlight: Mapping[str, str]
    ) -> ContextualizedHighlight | None:
        if "quote" not in highlight or highlight["quote"] is None:  # type: ignore
            return None

        return ContextualizedHighlight(
            source_doc_title=self.title,
            source_doc_uri=self.uri,
            highlighted_text=highlight["quote"],
            prefix=highlight["prefix"],
            suffix=highlight["suffix"],
            updated_at=highlight["updatedAt"],  # type: ignore
            source_highlight_uri=f"https://omnivore.app/me/{self.slug}#{highlight["id"]}",
        )

    def get_highlights(self) -> Iter[ContextualizedHighlight]:
        highlights = Iter(self.highlights).map(self._parse_highlight)
        return highlights.filter(lambda _: _ is not None)  # type: ignore
