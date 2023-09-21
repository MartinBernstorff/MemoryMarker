import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Union

import gpt2anki.data_access.fileio as fileio
from dotenv import load_dotenv
from gpt2anki.data_access.highlight_sources.base import HydratedHighlight
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.schema.output import LLMResult

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

@dataclass(frozen=True)
class HydratedPrompt:
    system_message: SystemMessage
    human_message: HumanMessage
    highlight: HydratedHighlight

def highlight_to_msg(highlight: HydratedHighlight) -> list[HydratedPrompt]:
    return [
       HydratedPrompt(system_message=SystemMessage(content=SYSTEM_PROMPT), human_message=HumanMessage(content=highlight_to_prompt(highlight)), highlight=highlight)
    ]

@dataclass(frozen=True)
class QAQuestion:
    question: str
    answer: str
    highlight: HydratedHighlight

def prompts_from_string(text: str, document_title: str) -> QAQuestion:
    start = text.find("{")
    end = text.rfind("}") + 1
    parsed_dict = ast.literal_eval(text[start:end])
    return QAQuestion(
        question=parsed_dict["question"],
        answer=parsed_dict["answer"],
    )


def parse_output(output: LLMResult) -> list[QAQuestion]:
    return [prompts_from_string(response[0].text) for response in output.generations]


async def prompt_gpt(
    model: ChatOpenAI,
    highlights: list[HydratedHighlight],
) -> list[QAQuestion]:
    messages = map(highlight_to_msg, highlights)
    output = await model.agenerate(messages=messages)

    return parse_output(output)
