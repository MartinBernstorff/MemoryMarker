from dataclasses import dataclass
from typing import TYPE_CHECKING

from memorymarker.question_generator.steps.step import FlowStep

if TYPE_CHECKING:
    from memorymarker.question_generator.completers.openai_completer import (
        ModelCompleter,
    )
    from memorymarker.question_generator.qa_responses import QAResponses
    from memorymarker.question_generator.reasoned_highlight import Highlights


@dataclass(frozen=True)
class QuestionExtractionStep(FlowStep):
    completer: "ModelCompleter"

    def identity(self) -> str:
        return f"{self.__class__.__name__}_{self.completer.identity()}"

    async def __call__(self, reasoned_highlight: "Highlights") -> "Highlights":
        responses: QAResponses = await self.completer(
            f"""Extract:
{reasoned_highlight.qa_string}
"""
        )  # type: ignore

        reasoned_highlight.question_answer_pairs = [
            item.to_qaprompt(reasoned_highlight) for item in responses.items
        ]
        return reasoned_highlight
