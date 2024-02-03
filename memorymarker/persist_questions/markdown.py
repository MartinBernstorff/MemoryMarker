import re
from pathlib import Path


from memorymarker.question_generator.question_generator import QAPrompt


def clean_filename(filename: str) -> str:
    # This will replace not allowed symbols with an underscore.
    return re.sub(r"[^A-Za-z]", "_", filename)


def q_to_markdown(prompt: QAPrompt) -> str:
    return f"""Q. {prompt.question}
A. {prompt.answer}
[Highlight]({prompt.hydrated_highlight.source_highlight_uri})
\n"""


def write_md(contents: str, file_title: str, save_dir: Path) -> None:
    """Write markdown to file. Append if exists"""
    save_dir.mkdir(exist_ok=True, parents=True)
    with (save_dir / f"{clean_filename(file_title)}.md").open(mode="a") as f:
        f.write(contents + "\n")


def write_qa_prompt_to_md(prompt: QAPrompt, save_dir: Path) -> None:
    """Write markdown to file. Append if exists"""
    contents = q_to_markdown(prompt)
    write_md(contents=contents, file_title=prompt.title, save_dir=save_dir)
