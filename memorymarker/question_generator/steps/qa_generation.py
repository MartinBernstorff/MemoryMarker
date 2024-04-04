from dataclasses import dataclass
from typing import TYPE_CHECKING

from memorymarker.question_generator.steps.step import FlowStep

if TYPE_CHECKING:
    from memorymarker.question_generator.completers.completer import Completer
    from memorymarker.question_generator.reasoned_highlight import Highlights


@dataclass(frozen=True)
class QuestionGenerationStep(FlowStep):
    completer: "Completer"
    n_questions: tuple[int, int]
    prompt = """You are generating interesting questions. The questions should:
* Create understanding: Prompts should foster understanding, activating related concepts and comparing them to one another. Focus especially on why concepts are related to each other, and how they differ. Feel free to ask questions that are challenging or that require deep thought.
* Be concise: Be as short as possible. Be clear, direct and brief.
* Be paraphrased: The questions should never quote the context.
* Be context-independent: The question must cue or supply all context that is necessary to understand the question. Questions must not assume that th user has read the text that generated the question.

Never refer to the text, quote or source:
BAD: According to the quote, why is [FACT]?
GOOD: Why is [FACT]?

Ensure that each pair only asks one question:
BAD:
Q. What is search time complexity of a singly linked list, and why?
A. O(n), because you have to visit each node once.

GOOD:
Q. What is the search time complexity of a singly linked list?
A. O(n)

Q. Why is the search time complexity of a singly linked list O(n)?
A. Because you have to visit each node once.

Never reuse the question in the answer:
BAD: Q. Why is criticism of men as a gender alone insufficient?
A. Criticism alone is not enough: It does not provide a solution, or show men what masculinity could be.

GOOD: Q. Why is criticism of men as a gender alone insufficient?
A. It does not provide a solution, or show men what masculinity could be.

Please generate between {lower_bound} and {upper_bound} question/answer pairs.

Document: "{document_title}"

{reasoning}

They should be formatted like:

Q. What is [FACT]?
A. [ANSWER]
"""

    def identity(self) -> str:
        return f"{self.__class__.__name__}_{self.completer.identity()}"

    async def __call__(self, highlight: "Highlights") -> "Highlights":
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
