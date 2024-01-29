from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


def read_txt(filepath: Path) -> str:
    """Read a text file."""
    return filepath.read_text(encoding="utf-8")
