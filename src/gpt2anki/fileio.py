from pathlib import Path


def read_txt(filepath: Path) -> str:
    """Read a text file."""
    with Path.open(filepath) as f:
        return f.read()
