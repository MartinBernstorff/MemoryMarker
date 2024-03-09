from dataclasses import dataclass

from memorymarker.question_generator.expanded_pipeline import Model, PipelineMiddleStep


@dataclass(frozen=True)
class StudentReflection(PipelineMiddleStep):
    model: Model
    base_name: str = "student-reflection"

    async def __call__(self, input_text: str) -> str:
        prompt = f"""A student is interested in learning the followign reasoning:

{input_text}

Write one or more questions intended to get a student to reflect on these points. Questions should include:

* Comparison to alternatives
* Pros and cons about the approach
* Example cases for reflection

For each question, also write a one-sentence answer."""

        return await self.model.create_completion(message=prompt)
