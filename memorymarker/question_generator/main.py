import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from iterpy.iter import Iter
from joblib import Memory

from memorymarker.document_providers.omnivore import Omnivore
from memorymarker.question_generator.example_repo_airtable import (
    PipelineHighlightIdentity,
)

if TYPE_CHECKING:
    from memorymarker.question_generator.flows.question_flow import QuestionFlow
    from memorymarker.question_generator.reasoned_highlight import Highlights

omnivore_cache = Memory(".cache/omnivore")


@dataclass(frozen=True)
class HighlightWithPipeline(PipelineHighlightIdentity):
    highlight: "Highlights"
    pipeline: "QuestionFlow"

    def identity(self) -> int:
        return self.pipeline_highlight_id(
            self.pipeline.identity, self.highlight.highlighted_text
        )


def _generate_highlight_pipeline_pairs(
    selected_highlights: Iter["Highlights"], pipelines: Sequence["QuestionFlow"]
) -> Iter[HighlightWithPipeline]:
    return Iter(
        [
            HighlightWithPipeline(highlight=highlight, pipeline=pipeline)
            for pipeline in pipelines
            for highlight in selected_highlights.to_list()
        ]
    )


@omnivore_cache.cache()  # type: ignore
def _select_highlights_from_omnivore() -> Iter["Highlights"]:
    highlights = (
        Omnivore(
            api_key=os.getenv("OMNIVORE_API_KEY", "No OMNIVORE_API_KEY in environment")
        )
        .get_documents()
        .map(lambda _: _.get_highlights().to_list())
        .flatten()
    )

    return highlights


def chunk_highlights(
    group: tuple[str, Sequence["Highlights"]], chunk_size: int
) -> Sequence["Highlights"]:
    groups: Sequence["Highlights"] = []

    for i in range(0, len(group[1]), 5):
        subset: Sequence["Highlights"] = group[1][i : i + chunk_size]
        combined_text = "\n---\n".join(
            f"> {_.prefix}<HIGHLIGHT>{_.highlighted_text}</HIGHLIGHT>{_.suffix}"
            for _ in subset
        )
        new_highlight = subset[-1]
        new_highlight.highlighted_text = combined_text
        new_highlight.prefix = ""
        new_highlight.suffix = ""
        groups.append(new_highlight)

    return groups
