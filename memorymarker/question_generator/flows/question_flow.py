from dataclasses import dataclass
from typing import TYPE_CHECKING

from iterpy.iter import Iter

if TYPE_CHECKING:
    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight
    from memorymarker.question_generator.steps.step import FlowStep


@dataclass(frozen=True)
class QuestionFlow:
    _name: str
    steps: tuple["FlowStep"]

    async def __call__(
        self, highlights: "Iter[ReasonedHighlight]"
    ) -> "Iter[ReasonedHighlight]":
        results: list[ReasonedHighlight] = highlights.to_list()
        for step in self.steps:
            results = [await step(highlight) for highlight in results]

        return Iter(results)

    @property
    def name(self) -> str:
        return f"{self._name}_{hash(self)}"
