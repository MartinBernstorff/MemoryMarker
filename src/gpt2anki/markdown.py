import hashlib
from pathlib import Path

SAVE_DIR = Path("card_cache")

def hash_uri(uri: str) -> str:
    """return an md5 hash of the uri"""
    return hashlib.md5(uri.encode()).hexdigest()
    

def q_to_markdown(question: dict[str, str]) -> str:
    return f"Q: {question['question']}\nA: {question['answer']}\n\n"


def write_md(markdown: str, origin_uri: str, save_dir: Path=SAVE_DIR) -> None:
    """Write markdown to file. Append if exists"""
    if not save_dir.exists():
        save_dir.mkdir()
    uri_filename = f"{hash_uri(origin_uri)}.md"
    with Path.open(SAVE_DIR / uri_filename, "a") as f:
        f.write(markdown)