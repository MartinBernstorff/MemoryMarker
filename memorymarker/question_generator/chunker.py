from typing import TYPE_CHECKING, Sequence

from joblib import Memory

if TYPE_CHECKING:
    from memorymarker.question_generator.reasoned_highlight import Highlights

omnivore_cache = Memory(".cache/omnivore")


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
