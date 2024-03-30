import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Type

import pytest

from memorymarker.question_generator.completers.openai_completer import (
    OpenAICompleter,
    OpenAIModelCompleter,
)
from memorymarker.question_generator.qa_responses import QAResponses
from memorymarker.question_generator.steps.qa_extractor import QuestionExtractionStep
from memorymarker.question_generator.steps.qa_generation import QuestionGenerationStep
from memorymarker.question_generator.steps.reasoning import ReasoningStep

if TYPE_CHECKING:
    from memorymarker.question_generator.steps.step import FlowStep


def gpt_4_completer() -> OpenAICompleter:
    return OpenAICompleter(
        api_key=os.getenv("OPENAI_API_KEY", "No OPENAI_API_KEY in environment"),
        model="gpt-4-turbo-preview",
    )


@dataclass
class Step:
    step: Type["FlowStep"]
    completer: OpenAICompleter | OpenAIModelCompleter = field(
        default_factory=gpt_4_completer
    )

    def __call__(self) -> "FlowStep":
        return self.step(completer=self.completer)


@pytest.mark.parametrize(
    ("step"),
    [
        Step(step=ReasoningStep),
        Step(step=QuestionGenerationStep),
        Step(
            step=QuestionExtractionStep,
            completer=OpenAIModelCompleter(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model="gpt-4-turbo-preview",
                response_model=QAResponses,  # type: ignore
            ),
        ),
    ],
)
def test_step_hashes_are_constant(step: Step, snapshot: str):
    assert step().identity() == snapshot
