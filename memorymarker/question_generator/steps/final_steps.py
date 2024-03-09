from dataclasses import dataclass
from typing import TYPE_CHECKING

from iterpy.iter import Iter

if TYPE_CHECKING:
    from memorymarker.question_generator.qa_prompt import QAPromptResponseModel


@dataclass(frozen=True)
class QuestionExtractor:
    base_name: str = "question-extractor"

    async def __call__(self, input_text: str) -> Iter["QAPromptResponseModel"]:
        prompt = f"""This is a set of questions and answers. Extract them to the following model.

        {input_text}"""

    # XXX: Implement question extractor
