import logging
import re
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from pathlib import Path

    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight


def clean_filename(filename: str) -> str:
    # This will replace not allowed symbols with an underscore.
    without_illegal = re.sub(r"[^A-Za-z\s]", " ", filename)
    without_duplicate_spaces = re.sub(r"\s{2,}", ", ", without_illegal)
    return without_duplicate_spaces


def highlight_group_to_file(
    output_dir: "Path", group: tuple[str, Sequence["ReasonedHighlight"]]
) -> None:
    save_path = output_dir / clean_filename(group[0])

    with save_path.open(mode="a") as f:
        for highlight in group[1]:
            f.write(highlight.to_markdown())
        f.write("\n---\n")

    logging.info(f"Wrote {group[0]}")
