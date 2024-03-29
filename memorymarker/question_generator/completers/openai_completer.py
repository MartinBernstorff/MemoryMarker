from dataclasses import dataclass
from typing import Literal

import instructor
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)

OPENAI_MODELS = Literal["gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-3.5-turbo"]

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import pydantic


class Completer(Protocol):
    async def __call__(self, prompt: str) -> str:
        ...


@dataclass
class OpenAICompleter:
    api_key: str
    model: OPENAI_MODELS

    def __post_init__(self):
        self.client = instructor.patch(AsyncOpenAI(api_key=self.api_key))
        self.completer = self.client.chat.completions

    async def __call__(self, prompt: str) -> str:
        completion = await self.completer.create(
            model=self.model,
            messages=[
                ChatCompletionUserMessageParam(
                    role="user", name="UserName", content=prompt
                )
            ],
            temperature=0.0,
        )
        completion_str = completion.choices[0].message.content

        if not completion_str:
            raise ValueError(f"Completion was not a string: {completion_str}")

        return completion_str


class ModelCompleter(Protocol):
    async def __call__(self, prompt: str) -> "pydantic.BaseModel":
        ...


@dataclass
class OpenAIModelCompleter(ModelCompleter):
    api_key: str
    model: OPENAI_MODELS
    response_model: "pydantic.BaseModel"

    def __post_init__(self):
        self.client = instructor.patch(AsyncOpenAI(api_key=self.api_key))
        self.completer = self.client.chat.completions

    async def __call__(self, prompt: str) -> "pydantic.BaseModel":
        completion = await self.completer.create(  # type: ignore
            model=self.model,
            messages=[
                ChatCompletionUserMessageParam(
                    role="user", name="UserName", content=prompt
                )
            ],
            temperature=0.0,
            response_model=self.response_model,
        )
        return completion  # type: ignore
