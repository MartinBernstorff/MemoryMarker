import ast
from pathlib import Path

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.schema.output import LLMResult
from dotenv import load_dotenv

import src.gpt2anki.fileio as fileio
from src.gpt2anki.sources.hypothesis import Highlight

load_dotenv()
SYSTEM_PROMPT = fileio.read_txt(Path("../prompts/martin_prompt.txt"))


def initialize_model() -> ChatOpenAI:
    return ChatOpenAI(model="gpt-4")


def highlight_to_prompt(highlight: Highlight) -> str:
    return "<target>{target}</target><context>{context}</context>".format(
        target=highlight.highlight,
        context=highlight.context,
    )


def parse_output(output: LLMResult) -> dict[str, str]:
    text_output = output.generations[0][0].text
    # extract dictionary from string
    start = text_output.find("{")
    end = text_output.rfind("}") + 1
    return ast.literal_eval(text_output[start:end])


async def prompt_gpt(
    model: ChatOpenAI,
    highlight: Highlight,
) -> dict[str, str]:
    prompt = highlight_to_prompt(highlight)
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
    output = await model.agenerate(messages=[messages])
    return parse_output(output)
