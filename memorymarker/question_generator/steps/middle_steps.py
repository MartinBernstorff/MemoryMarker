from dataclasses import dataclass

from memorymarker.question_generator.expanded_pipeline import Model, PipelineMiddleStep


@dataclass(frozen=True)
class StudentReflection(PipelineMiddleStep):
    model: Model
    variant: str

    async def __call__(self, input_text: str) -> str:
        prompt = f"""A student is interested in learning the following reasoning:

{input_text}

Write one or more questions to get the student to reflect. Questions should be about:

* Comparison to alternatives
* Pros and cons about the approach
* Example cases for reflection

Never ask the student to generate their own examples. Keep questions extremely brief, concise, and to the point. Students will not read long questions. Yet focus on reflection and elaboration."""

        return await self.model.create_completion(message=prompt)
