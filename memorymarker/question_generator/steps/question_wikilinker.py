import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from memorymarker.question_generator.steps.step import FlowStep

if TYPE_CHECKING:
    from memorymarker.question_generator.completers.completer import Completer
    from memorymarker.question_generator.qa_responses import QAPrompt
    from memorymarker.question_generator.reasoned_highlight import Highlights


@dataclass(frozen=True)
class QuestionWikilinker(FlowStep):
    completer: "Completer"
    prompt = """In the following, identify the important, domain-specific terms. Then, capitalise them, and surround them with wikilinks. There can be more than one important term. Identify terms as you would in a wikipedia article.

E.g.:
When working with version control, why is the git amend command misleading?

Turns into:
When working with [[Version control]], why is the [[Git amend]] command misleading?
Here is the question:
{question}
"""

    def identity(self) -> str:
        return f"{self.__class__.__name__}_{self.completer.identity()}"

    async def _wikilink_prompt(self, question: "QAPrompt") -> "QAPrompt":
        prompt = self.prompt.format(question=question.question)
        response = await self.completer(prompt)  # type: ignore
        question.question = response
        return question

    async def __call__(self, highlight: "Highlights") -> "Highlights":
        prompts = highlight.question_answer_pairs
        wikilinked_prompts = await asyncio.gather(
            *[self._wikilink_prompt(prompt) for prompt in prompts]
        )
        highlight.question_answer_pairs = wikilinked_prompts
        return highlight
