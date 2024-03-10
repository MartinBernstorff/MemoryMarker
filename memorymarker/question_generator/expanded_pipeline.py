import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, Sequence

from iterpy.iter import Iter
from openai import AsyncOpenAI

from memorymarker.question_generator.highlight_to_question import HighlightToQuestion

if TYPE_CHECKING:
    from memorymarker.document_providers.ContextualizedHighlight import (
        ContextualizedHighlight,
    )
    from memorymarker.question_generator.qa_prompt import (
        QAPrompt,
        QAPromptResponseModel,
    )
    from memorymarker.question_generator.steps.final_steps import QuestionExtractor


@dataclass
class Model(Protocol):
    api_key: str
    name: str

    async def create_completion(self, message: str) -> str:
        ...


@dataclass
class GPT4(Model):
    api_key: str
    name: str = "gpt-4-0125-preview"

    def __post_init__(self):
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def create_completion(self, message: str) -> str:
        return await self.client.chat.completions.create(
            model=self.name,
            messages=[{"role": "user", "content": message}],
            temperature=0.0,
        )  # type: ignore


class PipelineStep(ABC):
    model: Model
    base_name: str

    @property
    def name(self) -> str:
        return f"{self.base_name}-{self.model.name}"


class PipelineFirstStep(PipelineStep):
    @abstractmethod
    async def __call__(self, highlight: "ContextualizedHighlight") -> str:
        ...


class PipelineMiddleStep(PipelineStep):
    @abstractmethod
    async def __call__(self, input_text: str) -> str:
        ...


@dataclass(frozen=True)
class ExpandedPipeline(HighlightToQuestion):
    first_step: PipelineFirstStep
    steps: Sequence[PipelineMiddleStep]
    final_step: "QuestionExtractor"

    async def _highlight_to_question(
        self, highlight: "ContextualizedHighlight"
    ) -> "Iter[QAPromptResponseModel]":
        result = await self.first_step(highlight)

        for step in self.steps:
            result = await step(result)

        return await self.final_step(result)

    async def _gather(
        self, highlights: Iter["ContextualizedHighlight"]
    ) -> Iter["QAPromptResponseModel"]:
        questions = [self._highlight_to_question(highlight) for highlight in highlights]
        response = await asyncio.gather(*questions)
        return Iter(response).flatten()

    def __call__(self, highlights: "Iter[ContextualizedHighlight]") -> "Iter[QAPrompt]":
        response = asyncio.run(self._gather(highlights))

        hydrated_responses = response.zip(highlights).map(
            lambda qa_context_pair: qa_context_pair[0].to_qaprompt(qa_context_pair[1])
        )
        return hydrated_responses

    @property
    def name(self) -> str:
        name = self.first_step.name

        for step in self.steps:
            name += f"-{step.name}"

        name += f"-{self.final_step.name}"
        return name
