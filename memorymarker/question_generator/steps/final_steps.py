from dataclasses import dataclass
from typing import TYPE_CHECKING

from instructor import patch
from iterpy.iter import Iter  # noqa: TCH002
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)

from memorymarker.question_generator.qa_prompt import QAPromptResponseModel, QAResponses

if TYPE_CHECKING:
    from openai.types.chat.chat_completion_message_param import (
        ChatCompletionMessageParam,
    )


@dataclass
class QuestionExtractor:
    openai_api_key: str
    name: str = "question-extractor"
    model = "gpt-4-0125-preview"

    def __post_init__(self):
        self.client = patch(  # type: ignore # Incorrectly typed from Instructor library
            AsyncOpenAI(api_key=self.openai_api_key)
        )

    def _build_message(self, input_str: str) -> "ChatCompletionMessageParam":
        return ChatCompletionUserMessageParam(
            role="user",
            name="UserName",
            content=f"""This is a set of questions and answers. Extract them to the following model. {input_str}""",
        )

    async def __call__(self, input_str: str) -> Iter["QAPromptResponseModel"]:
        return await self.client.chat.completions.create(
            model=self.model,
            messages=[self._build_message(input_str=input_str)],
            response_model=QAResponses,
            temperature=0.0,
        )  # type: ignore
