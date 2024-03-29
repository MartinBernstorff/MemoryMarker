from dataclasses import dataclass
from typing import TYPE_CHECKING

from memorymarker.question_generator.steps.step import FlowStep

if TYPE_CHECKING:
    from memorymarker.question_generator.completers.openai_completer import Completer
    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight


@dataclass(frozen=True)
class ReasoningStep(FlowStep):
    completer: "Completer"

    async def __call__(self, highlight: "ReasonedHighlight") -> "ReasonedHighlight":
        prompt = f"""You are a teacher at a university, helping students understand what and why a concept is important.

This is a highlight from a document titled "{highlight.source_document.title}", which the student found important.

{highlight.context}

Think through why the student should be interested in this concept, and what they can learn from it. Think step by step, one bullet point at a time, with at least 5 bullet points. Each bullet point should be brief.

Ask "Why is that?" at the beginning of each bullet point.
"""

        reasoning = await self.completer(prompt)
        highlight.reasoning = reasoning
        highlight.reasoning_prompt = prompt

        return highlight
