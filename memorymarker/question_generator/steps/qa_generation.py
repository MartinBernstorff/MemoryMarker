from dataclasses import dataclass
from typing import TYPE_CHECKING

from memorymarker.question_generator.steps.step import FlowStep

if TYPE_CHECKING:
    from memorymarker.question_generator.completers.completer import Completer
    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight


@dataclass(frozen=True)
class QuestionGenerationStep(FlowStep):
    completer: "Completer"
    n_questions: tuple[int, int] = (1, 5)
    prompt = """You are generating interesting questions. The questions should:
* Create understanding: Prompts should foster understanding, activating related concepts and comparing them to one another. Focus especially on why concepts are related to each other, and how they differ. Feel free to ask questions that are challenging or that require deep thought.
* Be concise: Be as short as possible. Be clear, direct and brief.
* Be paraphrased: The questions should never quote the context.
* Be context-independent: The question must cue or supply all context that is necessary to understand the question. Questions must not assume that th user has read the text that generated the question. It should not address the text or use the context of the text in any way.

Document: "{document_title}"

{reasoning}

Please generate between {lower_bound} and {upper_bound} question/answer pairs to reinforce understanding of the concept.

They should be formatted like:

Q. What is the meaning of life?
A. 42
"""

    def identity(self) -> str:
        return f"{self.__class__.__name__}_{self.completer.identity()}"

    async def __call__(self, highlight: "ReasonedHighlight") -> "ReasonedHighlight":
        prompt = self.prompt.format(
            document_title=highlight.source_document.title,
            reasoning=f"""{highlight.reasoning}""" if highlight.reasoning else "",
            lower_bound=self.n_questions[0],
            upper_bound=self.n_questions[1],
        )

        response = await self.completer(prompt)
        highlight.qa_string = response
        highlight.reasoning_prompt = prompt

        return highlight
