from dataclasses import dataclass
from typing import Literal

import anthropic

from memorymarker.question_generator.completers.completer import Completer

ANTHROPIC_MODELS = Literal[
    "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
]


@dataclass
class AnthropicCompleter(Completer):
    api_key: str | None
    model: ANTHROPIC_MODELS

    def identity(self) -> str:
        return f"{self.__class__.__name__}_{self.model}"

    def __post_init__(self):
        if self.api_key is None:
            raise ValueError("API key is required")

        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def __call__(self, prompt: str) -> str:
        completion = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        completion_str = "\n".join(message.text for message in completion.content)

        if not completion_str:
            raise ValueError(f"Completion was not a string: {completion_str}")

        return completion_str
