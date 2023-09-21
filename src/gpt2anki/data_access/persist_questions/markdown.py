from pathlib import Path

from gpt2anki.domain.highlights_to_questions import QAPrompt

SAVE_DIR = Path("card_cache")

import re


def clean_filename(filename: str) -> str:
    # This will replace not allowed symbols with an underscore.
    return re.sub(r"[^A-Za-z]", "_", filename)


def q_to_markdown(prompt: QAPrompt) -> str:
    return f"Q. {prompt.question}\nA. {prompt.answer}\n\n"


def write_md(contents: str, origin_uri: str, save_dir: Path = SAVE_DIR) -> None:
    """Write markdown to file. Append if exists"""
    if not save_dir.exists():
        save_dir.mkdir()
    uri_filename = f"{clean_filename(origin_uri)}.md"
    with Path.open(SAVE_DIR / uri_filename, "a") as f:
        f.write(contents)
