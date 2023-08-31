from pathlib import Path
from langchain.chat_models import ChatOpenAI

import src.gpt2anki.fileio as fileio
from src.gpt2anki.sources.base import Highlight


PROMPT = fileio.read_txt(Path("../prompts/martin_prompt.txt"))

def initialize_model() -> ChatOpenAI:
    return ChatOpenAI(model="gpt-4")


