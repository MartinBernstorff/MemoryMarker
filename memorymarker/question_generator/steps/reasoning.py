from dataclasses import dataclass
from typing import TYPE_CHECKING

from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight
from memorymarker.question_generator.steps.step import FlowStep

if TYPE_CHECKING:
    from memorymarker.question_generator.completers.openai_completer import Completer


@dataclass(frozen=True)
class ReasoningStep(FlowStep):
    completer: "Completer"

    async def __call__(self, highlight: "ReasonedHighlight") -> "ReasonedHighlight":
        prompt = f"""You are a teacher at a university, helping students understand what and why a concept is important.

This is a highlight from a document titled "{highlight.highlight.source_doc_title}", which the student found important.

{highlight.highlight.context}

Think through why the student should be interested in this concept, and what they can learn from it. Think step by step, one bullet point at a time, with at least 5 bullet points. Each bullet point should be brief.

Ask "Why is that?" at the beginning of each bullet point.
"""

        reasoning = await self.completer(prompt)
        return ReasonedHighlight(
            highlight=highlight.highlight,
            reasoning=reasoning,
            reasoning_prompt=prompt,
            question_answer_pairs=highlight.question_answer_pairs,
            pipeline_name=highlight.pipeline_name,
            qa_string="",
        )
