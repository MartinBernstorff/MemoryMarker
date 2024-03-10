from typing import Sequence

from iterpy.iter import Iter

from memorymarker.question_generator.question_generator_evaluator.types import (
    HighlightWithPipeline,
    QAPromptWithPipeline,
)


def run_pipelines(
    pairs: "Iter[HighlightWithPipeline]",
) -> Sequence["QAPromptWithPipeline"]:
    pipelinename2pipeline = {pair.pipeline.name: pair.pipeline for pair in pairs}

    pipelines_with_highlights = pairs.groupby(lambda _: _.pipeline.name)

    examples: Sequence[QAPromptWithPipeline] = []
    for pipeline_name, pair in pipelines_with_highlights:
        print(f"Creating examples for {pipeline_name}")
        pipeline = pipelinename2pipeline[pipeline_name]

        highlights = [pair.highlight for pair in pair]
        prompts = pipeline(Iter(highlights))

        for prompt in prompts:
            examples.append(
                QAPromptWithPipeline(prompt=prompt, pipeline_name=pipeline_name)
            )

    return examples
