from pathlib import Path


def read_txt(filepath: Path) -> str:
    """Read a text file."""
    return filepath.read_text(encoding="utf-8")
