from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from iterpy.iter import Iter

if TYPE_CHECKING:
    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight
    from memorymarker.question_generator.steps.step import FlowStep


@dataclass
class QuestionFlow:
    _name: str
    steps: Sequence["FlowStep"]

    async def __call__(
        self, highlights: "Iter[ReasonedHighlight]"
    ) -> "Iter[ReasonedHighlight]":
        results: list[ReasonedHighlight] = highlights.to_list()
        for step in self.steps:
            results = [await step(highlight) for highlight in results]

        return Iter(results)

    @property
    def name(self) -> str:
        return self._name
