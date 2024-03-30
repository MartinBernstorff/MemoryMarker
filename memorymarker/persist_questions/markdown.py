import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight


def _clean_filename(filename: str) -> str:
    # This will replace not allowed symbols with an underscore.
    without_illegal = re.sub(r"[^A-Za-z\s]", " ", filename)
    without_duplicate_spaces = re.sub(r"\s{2,}", ", ", without_illegal)
    return without_duplicate_spaces


def write_qa_prompt_to_md(highlight: "ReasonedHighlight", save_dir: "Path") -> None:
    """Write markdown to file. Append if exists"""
    with (save_dir / f"{_clean_filename(highlight.source_document.title)}.md").open(
        mode="a"
    ) as f:
        f.write(highlight.to_markdown())
