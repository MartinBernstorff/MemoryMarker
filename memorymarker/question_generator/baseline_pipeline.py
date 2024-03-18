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
from memorymarker.question_generator.qa_responses import QAPromptResponseModel

if TYPE_CHECKING:
    from memorymarker.document_providers.contextualized_highlight import (
        ContextualizedHighlight,
    )

PROMPT_DIR = Path(__file__).parent.parent / "prompts"
assert PROMPT_DIR.exists(), f"Prompts directory does not exist at {PROMPT_DIR}"
SYSTEM_PROMPT = (PROMPT_DIR / "martin_prompt.txt").read_text()


from iterpy.iter import Iter

from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight

OPENAI_MODELS = Literal["gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-3.5-turbo"]


@dataclass
class BaselinePipeline(HighlightToQuestion):
    _name: str
    openai_api_key: str
    model: OPENAI_MODELS
    prompt: str = SYSTEM_PROMPT

    @property
    def name(self) -> str:
        return self._name

    def __post_init__(self):
        self.client = instructor.patch(
            AsyncOpenAI(api_key=self.openai_api_key)  # type: ignore # Incorrectly typed from Instructor library
        )

    async def _highlight_to_qa(
        self, highlight: "ContextualizedHighlight"
    ) -> "QAPromptResponseModel":
        return await self.client.chat.completions.create(
            model=self.model,
            messages=[
                ChatCompletionUserMessageParam(
                    role="user",
                    name="UserName",
                    content=f"""{self.prompt}

The highlight is from a document titled "{highlight.source_doc_title}".

{highlight.context}""",
                )
            ],
            response_model=QAPromptResponseModel,  # type: ignore
            temperature=0.0,
        )  # type: ignore

    async def _highlights_to_qa(
        self, highlights: Sequence["ContextualizedHighlight"]
    ) -> Sequence["QAPromptResponseModel"]:
        questions = [self._highlight_to_qa(highlight) for highlight in highlights]
        response = await asyncio.gather(*questions)
        return response

    def __call__(
        self, highlights: "Iter[ContextualizedHighlight]"
    ) -> "Iter[ReasonedHighlight]":
        response: Sequence[QAPromptResponseModel] = asyncio.run(
            self._highlights_to_qa(highlights)  # type: ignore
        )

        hydrated_responses = (
            Iter(response)
            .zip(highlights.to_list())  # type: ignore
            .map(
                lambda qa_context_pair: qa_context_pair[0].to_qaprompt(  # type: ignore
                    qa_context_pair[1]  # type: ignore
                )
            )
            .map(
                lambda qa_prompts: ReasonedHighlight(
                    highlight=qa_prompts.hydrated_highlight,
                    reasoning=None,
                    question_answer_pairs=[qa_prompts],
                    pipeline_name=self.name,
                )
            )
        )
        return hydrated_responses
