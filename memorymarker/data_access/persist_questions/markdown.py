from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from memorymarker.domain.highlights_to_questions import QAPrompt

SAVE_DIR = Path("card_cache")

import re


def clean_filename(filename: str) -> str:
    # This will replace not allowed symbols with an underscore.
    return re.sub(r"[^A-Za-z]", "_", filename)


def q_to_markdown(prompt: QAPrompt) -> str:
    return f"Q. {prompt.question}\nA. {prompt.answer}\n\n"


def write_md(contents: str, file_title: str, save_dir: Path = SAVE_DIR) -> None:
    """Write markdown to file. Append if exists"""
    if not save_dir.exists():
        save_dir.mkdir()
    filename = f"{clean_filename(file_title)}.md"
    with Path.open(SAVE_DIR / filename, "a") as f:
        f.write(contents)


def write_qa_prompt_to_md(prompt: QAPrompt, save_dir: Path = SAVE_DIR) -> None:
    """Write markdown to file. Append if exists"""
    contents = q_to_markdown(prompt)
    write_md(contents=contents, file_title=prompt.title, save_dir=save_dir)
