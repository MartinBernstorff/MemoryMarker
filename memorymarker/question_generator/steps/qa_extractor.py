from dataclasses import dataclass
from typing import TYPE_CHECKING

from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight
from memorymarker.question_generator.steps.step import FlowStep

if TYPE_CHECKING:
    from memorymarker.question_generator.completers.openai_completer import (
        ModelCompleter,
    )
    from memorymarker.question_generator.qa_responses import QAResponses


@dataclass(frozen=True)
class QuestionExtractionStep(FlowStep):
    completer: "ModelCompleter"

    async def __call__(self, highlight: "ReasonedHighlight") -> ReasonedHighlight:
        responses: QAResponses = await self.completer(
            f"""Extract:
{highlight.qa_string}
"""
        )  # type: ignore

        return ReasonedHighlight(
            source_document=highlight.source_document,
            qa_string=highlight.qa_string,
            highlight=highlight.highlight,
            reasoning=highlight.reasoning,
            reasoning_prompt=highlight.reasoning_prompt,
            question_answer_pairs=[
                item.to_qaprompt(highlight.highlight) for item in responses.items
            ],
            pipeline_name=highlight.pipeline_name,
        )
