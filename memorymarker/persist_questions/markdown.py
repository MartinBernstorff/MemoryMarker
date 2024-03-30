import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from memorymarker.question_generator.qa_responses import QAPrompt
    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight


def _clean_filename(filename: str) -> str:
    # This will replace not allowed symbols with an underscore.
    without_illegal = re.sub(r"[^A-Za-z\s]", " ", filename)
    without_duplicate_spaces = re.sub(r"\s{2,}", ", ", without_illegal)
    return without_duplicate_spaces


def q_to_markdown(prompt: "QAPrompt") -> str:
    highlight = prompt.hydrated_highlight
    return f"""Q) {prompt.question}

> [!NOTE]- Highlight
> {highlight.prefix + " " or ""}=={highlight.highlighted_text}=={highlight.suffix.strip() + " " or ""}
> [Link]({highlight.source_document.uri})
\n"""


def write_qa_prompt_to_md(highlight: "ReasonedHighlight", save_dir: "Path") -> None:
    """Write markdown to file. Append if exists"""
    contents = "/n".join(
        [q_to_markdown(prompt) for prompt in highlight.question_answer_pairs]
    )

    with (save_dir / f"{_clean_filename(highlight.source_document.title)}.md").open(
        mode="a"
    ) as f:
        f.write(contents + "\n")
