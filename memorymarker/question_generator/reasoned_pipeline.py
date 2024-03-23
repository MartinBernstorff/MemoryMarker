import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import instructor
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_user_message_param import (
    ChatCompletionUserMessageParam,
)

from memorymarker.question_generator.highlight_to_question import HighlightToQuestion
from memorymarker.question_generator.qa_responses import QAResponses

if TYPE_CHECKING:
    from memorymarker.document_providers.contextualized_highlight import (
        ContextualizedHighlight,
    )

PROMPT_DIR = Path(__file__).parent.parent / "prompts"
assert PROMPT_DIR.exists(), f"Prompts directory does not exist at {PROMPT_DIR}"

from iterpy.iter import Iter

from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight

OPENAI_MODELS = Literal["gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-3.5-turbo"]


@dataclass
class ReasonedPipeline(HighlightToQuestion):
    _name: str
    openai_api_key: str
    model: OPENAI_MODELS
    prompt: str = (PROMPT_DIR / "martin_prompt.txt").read_text()  # noqa: RUF009

    @property
    def name(self) -> str:
        return self._name

    def __post_init__(self):
        self.client = instructor.patch(
            AsyncOpenAI(api_key=self.openai_api_key)  # type: ignore # Incorrectly typed from Instructor library
        )

    def _get_reasoning_prompt(self, highlight: "ContextualizedHighlight") -> str:
        return f"""You are a teacher at a university, helping students understand what and why a concept is important.

This is a highlight from a document titled "{highlight.source_doc_title}", which the student found important.

{highlight.context}

Think through why the student should be interested in this concept, and what they can learn from it. Think step by step, one bullet point at a time, with at least 5 bullet points. Each bullet point should be brief.

Ask "Why is that?" at the beginning of each bullet point.
"""

    async def _highlight_to_qa(
        self, highlight: "ContextualizedHighlight"
    ) -> Iter[ReasonedHighlight]:
        completions = self.client.chat.completions
        reasoning = await completions.create(
            model=self.model,
            messages=[
                ChatCompletionUserMessageParam(
                    role="user",
                    name="UserName",
                    content=self._get_reasoning_prompt(highlight),
                )
            ],
            temperature=0.0,
        )
        reasoning_str = reasoning.choices[0].message.content

        qa = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                ChatCompletionUserMessageParam(
                    role="user",
                    name="UserName",
                    content=f"""{self.prompt}

                    A student has highlighted the following text from a document titled "{highlight.source_doc_title}":

{highlight.highlighted_text}

The student found it important because:

{reasoning_str}

Please generate one or more question/answer pairs to reinforce the student's understanding of the concept.

They should be formatted like:

Q. What is the meaning of life?
A. 42
""",
                )
            ],
            temperature=0.0,
        )
        qa_string = qa.choices[0].message.content

        qa_responses: QAResponses = await completions.create(  # type: ignore
            model=self.model,
            messages=[
                ChatCompletionUserMessageParam(
                    role="user",
                    name="UserName",
                    content=f"""The following is a question/answer pairs. Extract them.
                    {qa_string}
""",
                )
            ],
            response_model=QAResponses,
            temperature=0.0,
        )

        return Iter(qa_responses.items).map(  # type: ignore
            lambda qa_response: ReasonedHighlight(
                highlight=highlight,
                reasoning=reasoning_str if reasoning_str is not None else "",
                reasoning_prompt=self._get_reasoning_prompt(highlight),
                question_answer_pairs=[qa_response.to_qaprompt(highlight)],
                pipeline_name=self.name,
            )
        )

    async def __call__(
        self, highlights: "Iter[ContextualizedHighlight]"
    ) -> "Iter[ReasonedHighlight]":
        questions = [self._highlight_to_qa(highlight) for highlight in highlights]
        response = await asyncio.gather(*questions)
        return Iter(response).flatten()
