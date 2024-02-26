from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from memorymarker.question_generator.prompts_from_string import llmresult_to_qas

if TYPE_CHECKING:
    from memorymarker.document_providers.ContextualizedHighlight import (
        ContextualizedHighlight,
    )

PROMPT_DIR = Path(__file__).parent.parent / "prompts"
assert PROMPT_DIR.exists(), f"Prompts directory does not exist at {PROMPT_DIR}"
SYSTEM_PROMPT = (PROMPT_DIR / "martin_prompt.txt").read_text()


def initialize_model(model_name: str = "gpt-4") -> ChatOpenAI:
    return ChatOpenAI(model=model_name)


@dataclass(frozen=True)
class HydratedOpenAIPrompt:
    system_message: SystemMessage
    human_message: HumanMessage
    highlight: "ContextualizedHighlight"


def _highlight_to_msg(highlight: "ContextualizedHighlight") -> HydratedOpenAIPrompt:
    human_message = "<target>{target}</target><context>{context}</context>".format(
        target=highlight.highlighted_text, context=highlight.context
    )
    return HydratedOpenAIPrompt(
        system_message=SystemMessage(content=SYSTEM_PROMPT),
        human_message=HumanMessage(content=human_message),
        highlight=highlight,
    )


@dataclass(frozen=True)
class QAPrompt:
    hydrated_highlight: "ContextualizedHighlight"
    question: str
    answer: str
    title: str


def _finalise_hydrated_questions(
    zipped_outputs: tuple[dict[str, str], HydratedOpenAIPrompt],
) -> QAPrompt:
    match zipped_outputs:
        case (model_outputs, hydrated_prompt):
            return QAPrompt(
                question=model_outputs["question"],
                answer=model_outputs["answer"],
                title=hydrated_prompt.highlight.source_doc_title,
                hydrated_highlight=hydrated_prompt.highlight,
            )


async def _prompts_to_questions(
    hydrated_prompts: list[HydratedOpenAIPrompt], model: ChatOpenAI
) -> list[QAPrompt]:
    prompts = [[x.human_message, x.system_message] for x in hydrated_prompts]

    model_output = await model.agenerate(messages=prompts)  # type: ignore
    parsed_outputs = llmresult_to_qas(model_output)

    zipped_outputs = zip(parsed_outputs, hydrated_prompts, strict=True)
    return list(map(_finalise_hydrated_questions, zipped_outputs))


async def highlights_to_questions(
    model: ChatOpenAI, highlights: Sequence["ContextualizedHighlight"]
) -> Sequence[QAPrompt]:
    hydrated_prompts = [_highlight_to_msg(x) for x in highlights]

    questions = await _prompts_to_questions(
        hydrated_prompts=hydrated_prompts, model=model
    )

    return questions
