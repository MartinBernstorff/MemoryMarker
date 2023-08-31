from pathlib import Path

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.schema.output import LLMResult

import src.gpt2anki.fileio as fileio
from src.gpt2anki.sources.hypothesis import Highlight

SYSTEM_PROMPT = fileio.read_txt(Path("../prompts/martin_prompt.txt"))


def initialize_model() -> ChatOpenAI:
    return ChatOpenAI(model="gpt-4")


def highlight_to_prompt(highlight: Highlight) -> str:
    return "<target>{target}</target><context>{context}</context>".format(
        target=highlight.highlight, context=highlight.context,
    )


async def prompt_gpt(model: ChatOpenAI, highlight: Highlight) -> LLMResult:
    prompt = highlight_to_prompt(highlight)
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
    output = model.agenerate(messages=[messages])
    return output
