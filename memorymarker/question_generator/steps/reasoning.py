from dataclasses import dataclass
from typing import TYPE_CHECKING

from memorymarker.question_generator.steps.step import FlowStep

if TYPE_CHECKING:
    from memorymarker.question_generator.completers.completer import Completer
    from memorymarker.question_generator.reasoned_highlight import Highlights


@dataclass(frozen=True)
class Reasoning(FlowStep):
    completer: "Completer"
    prompt = """Document title: {document_title}

Content: {context}

Think through the point made in the content. Think step by step.
"""

    def identity(self) -> str:
        return f"{self.__class__.__name__}_{self.completer.identity()}"

    async def __call__(self, highlight: "Highlights") -> "Highlights":
        prompt = self.prompt.format(
            document_title=highlight.source_document.title,
            context=highlight.highlighted_text,
        )

        reasoning = await self.completer(prompt)
        highlight.reasoning = reasoning
        highlight.reasoning_prompt = prompt

        return highlight
