from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Union

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, SystemMessage

import gpt2anki.data_access.fileio as fileio
from gpt2anki.data_access.highlight_sources.base import HydratedHighlight
from gpt2anki.domain.prompts_from_string import llmresult_to_qas

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


def highlight_to_msg(highlight: HydratedHighlight, model: ChatOpenAI) -> list[HydratedPrompt]:
    prompt = HydratedPrompt(system_message=SystemMessage(content=SYSTEM_PROMPT), human_message=HumanMessage(content=highlight_to_prompt(highlight)), highlight=highlight)

@dataclass(frozen=True)
class QAPrompt:
    question: str
    answer: str
    title: str

async def prompts_to_questions(hydrated_prompts: Generator[HydratedPrompt, None, None], model: ChatOpenAI) -> Generator[QAPrompt, None, None]:
    prompts = [[x.human_message, x.system_message] for x in hydrated_prompts]

    model_output = await model.agenerate(messages=prompts)
    parsed_outputs = llmresult_to_qas(model_output)

    zipped_outputs = zip(parsed_outputs, hydrated_prompts)

    return (QAPrompt(question=x[0]["Question"], answer=x[0]["Answer"], title=x[1].highlight.title) for x in zipped_outputs)

async def highlights_to_questions(
    model: ChatOpenAI,
    highlights: list[HydratedHighlight],
) -> list[QAPrompt]:
    hydrated_prompts = (highlight_to_msg(x, model=model) for x in highlights)
    
    questions = prompts_to_questions(hydrated_prompts=hydrated_prompts, model=model)

    return list(questios)
    
