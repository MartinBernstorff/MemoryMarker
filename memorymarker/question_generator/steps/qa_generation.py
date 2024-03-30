from dataclasses import dataclass
from typing import TYPE_CHECKING

from memorymarker.question_generator.steps.step import FlowStep

if TYPE_CHECKING:
    from memorymarker.question_generator.completers.openai_completer import Completer
    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight


@dataclass(frozen=True)
class QuestionGenerationStep(FlowStep):
    completer: "Completer"
    prompt = """You are a teacher creating spaced repetition prompts to reinforce knowledge from a student.

Your goals are to:
* Create perspective: The questions should relate concepts to one another, comparing alternate solutions to a given problem if possible.
* Create understanding: Prompts should foster understanding, activating related concepts and comparing them to one another. Focus especially on why concepts are related to each other, and how they differ.
* Be concise: Questions and answers should be as short as possible. Be clear, direct, even curt, and don't state anything in the answer that could be inferred from the question.
* Be paraphrased: The questions should never quote the context.
* Be context-independent: In review, this prompt will be interleaved with many others about many topics. The prompt must cue or supply whatever context is necessary to understand the question. They should not assume one has read the text that generated the prompts. It shouldn't address the text or use the context of the text in any way.
* Never focus on definitions, but instead on application and comparison.

The entire response should be at most 20 words. First, think step by step about why the person has highlighted this text. Then, write a question that, when reflected upon, produces maximum learning.


                    A student has highlighted the following text from a document titled "{document_title}":

{highlighted_text}

The student found it important because:

{reasoning}

Please generate one or more question/answer pairs to reinforce the student's understanding of the concept.

They should be formatted like:

Q. What is the meaning of life?
A. 42
"""

    def identity(self) -> str:
        return f"{self.__class__.__name__}_{self.completer.identity()}"

    async def __call__(self, highlight: "ReasonedHighlight") -> "ReasonedHighlight":
        prompt = self.prompt.format(
            document_title=highlight.source_document.title,
            highlighted_text=highlight.highlighted_text,
            reasoning=highlight.reasoning,
        )

        response = await self.completer(prompt)
        highlight.qa_string = response
        highlight.reasoning_prompt = prompt

        return highlight
