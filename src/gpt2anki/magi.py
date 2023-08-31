import ast
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.schema.output import LLMResult

import gpt2anki.fileio as fileio
from gpt2anki.sources.hypothesis import Highlight

load_dotenv()
print(Path(__file__))
PROMPT_DIR = Path(__file__).parent.parent.parent / "prompts"
assert PROMPT_DIR.exists(), "Prompts directory does not exist"
SYSTEM_PROMPT = fileio.read_txt(PROMPT_DIR / "martin_prompt.txt")


def initialize_model(model_name: str = "gpt-4") -> ChatOpenAI:
    return ChatOpenAI(model=model_name)


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
