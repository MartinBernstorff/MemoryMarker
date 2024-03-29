from typing import Any, Mapping, Sequence

from iterpy.iter import Iter
from pydantic import BaseModel

from memorymarker.question_generator.reasoned_highlight import (
    ReasonedHighlight,
    SourceDocument,
)


def empty_string_if_none(value: str | None) -> str:
    return value or ""


class OmnivoreDocument(BaseModel):
    title: str
    uri: str
    slug: str
    highlights: Sequence[Mapping[str, Any]]

    def _parse_highlight(
        self, highlight: Mapping[str, str]
    ) -> ReasonedHighlight | None:
        if "quote" not in highlight or highlight["quote"] is None:  # type: ignore
            return None

        return ReasonedHighlight(
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
            prefix=empty_string_if_none(highlight["prefix"]),
            suffix=empty_string_if_none(highlight["suffix"]),
            updated_at=highlight["updatedAt"],  # type: ignore # Will be recast on init.
        )

    def get_highlights(self) -> Iter[ReasonedHighlight]:
        highlights = Iter(self.highlights).map(self._parse_highlight)
        return highlights.filter(lambda _: _ is not None)  # type: ignore
