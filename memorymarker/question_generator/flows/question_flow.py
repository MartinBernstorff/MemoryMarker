import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from iterpy.iter import Iter

if TYPE_CHECKING:
    from memorymarker.question_generator.reasoned_highlight import Highlights
    from memorymarker.question_generator.steps.step import FlowStep

sem = asyncio.Semaphore(4)


@dataclass(frozen=True)
class QuestionFlow:
    _name: str
    steps: tuple["FlowStep"]

    async def _process_item(self, highlight: "Highlights") -> "Highlights":
        result = highlight
        async with sem:
            for step in self.steps:
                result = await step(highlight)
        result.pipeline_name = self.name
        return result

    async def __call__(self, highlights: Iter["Highlights"]) -> Iter["Highlights"]:
        results = await asyncio.gather(
            *[self._process_item(highlight) for highlight in highlights]
        )

        return Iter(results)

    @property
    def name(self) -> str:
        step_identites = "_".join(step.identity() for step in self.steps)
        return f"{self._name}_{step_identites}"
