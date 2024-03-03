import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Sequence

import instructor
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)

from memorymarker.question_generator.highlight_to_question import HighlightToQuestion

if TYPE_CHECKING:
    from openai.types.chat.chat_completion_message_param import (
        ChatCompletionMessageParam,
    )

    from memorymarker.document_providers.ContextualizedHighlight import (
        ContextualizedHighlight,
    )
    from memorymarker.question_generator.qa_prompt import QAPrompt

PROMPT_DIR = Path(__file__).parent.parent / "prompts"
assert PROMPT_DIR.exists(), f"Prompts directory does not exist at {PROMPT_DIR}"
SYSTEM_PROMPT = (PROMPT_DIR / "martin_prompt.txt").read_text()


from iterpy.iter import Iter

from memorymarker.question_generator.qa_prompt import QAPromptResponseModel

OPENAI_MODELS = Literal[
    "gpt-4-0125-preview",
    "gpt-4-turbo-preview",
    "gpt-4-1106-preview",
    "gpt-4-vision-preview",
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-0613",
    "gpt-4-32k",
    "gpt-4-32k-0314",
    "gpt-4-32k-0613",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-16k-0613",
]


@dataclass
class BaselinePipeline(HighlightToQuestion):
    openai_api_key: str
    model: OPENAI_MODELS
    prompt: str = SYSTEM_PROMPT

    def __post_init__(self):
        self.client = instructor.patch(  # type: ignore # Incorrectly typed from Instructor library
            AsyncOpenAI(api_key=self.openai_api_key)
        )

    def _build_message(
        self, highlight: "ContextualizedHighlight"
    ) -> "ChatCompletionMessageParam":
        return ChatCompletionUserMessageParam(
            role="user",
            name="Martin",
            content=f"""{self.prompt}

<target>{highlight.highlighted_text}</target><context>{highlight.context}</context>""",
        )

    async def _highlight_to_question(
        self, highlight: "ContextualizedHighlight"
    ) -> "QAPromptResponseModel":
        return await self.client.chat.completions.create(
            model=self.model,
            messages=[self._build_message(highlight=highlight)],
            response_model=QAPromptResponseModel,
            temperature=0.0,
        )  # type: ignore

    async def _gather(
        self, highlights: Sequence["ContextualizedHighlight"]
    ) -> Sequence["QAPromptResponseModel"]:
        questions = [self._highlight_to_question(highlight) for highlight in highlights]
        response = await asyncio.gather(*questions)
        return response

    def __call__(self, highlights: "Iter[ContextualizedHighlight]") -> "Iter[QAPrompt]":
        response: Sequence[QAPromptResponseModel] = asyncio.run(
            self._gather(highlights)  # type: ignore
        )

        hydrated_responses = (
            Iter(response)
            .zip(highlights.to_list())  # type: ignore
            .map(
                lambda qa_context_pair: qa_context_pair[0].to_qaprompt(  # type: ignore
                    qa_context_pair[1]  # type: ignore
                )
            )
        )
        return hydrated_responses
