import ast
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.schema.output import LLMResult

import gpt2anki.fileio as fileio
from gpt2anki.sources.base import HydratedHighlight

load_dotenv()
PROMPT_DIR = Path(__file__).parent.parent.parent / "prompts"
assert PROMPT_DIR.exists(), "Prompts directory does not exist"
SYSTEM_PROMPT = fileio.read_txt(PROMPT_DIR / "martin_prompt.txt")


def initialize_model(model_name: str = "gpt-4") -> ChatOpenAI:
    return ChatOpenAI(model=model_name)


def highlight_to_prompt(highlight: HydratedHighlight) -> str:
    return "<target>{target}</target><context>{context}</context>".format(
        target=highlight.highlight,
        context=highlight.context,
    )


def highlight_to_msg(highlight: HydratedHighlight) -> list[BaseMessage]:
    return [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=highlight_to_prompt(highlight)),
    ]


def dict_from_string(text: str) -> dict[str, str]:
    start = text.find("{")
    end = text.rfind("}") + 1
    return ast.literal_eval(text[start:end])


def parse_output(output: LLMResult) -> list[dict[str, str]]:
    return [dict_from_string(response[0].text) for response in output.generations]


async def prompt_gpt(
    model: ChatOpenAI,
    highlights: HydratedHighlight | list[HydratedHighlight],
) -> list[dict[str, str]]:
    if isinstance(highlights, HydratedHighlight):
        highlights = [highlights]
    messages = [highlight_to_msg(highlight) for highlight in highlights]
    output = await model.agenerate(messages=messages)
    return parse_output(output)
