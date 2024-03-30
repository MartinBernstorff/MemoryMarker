import logging
from typing import TYPE_CHECKING, Mapping, Sequence

from iterpy.iter import Iter

if TYPE_CHECKING:
    from memorymarker.question_generator.flows.question_flow import QuestionFlow
    from memorymarker.question_generator.main import HighlightWithPipeline
    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight


async def run_pipeline(
    pipeline_name: str,
    pipelinename2pipeline: Mapping[str, "QuestionFlow"],
    highlights: Sequence["ReasonedHighlight"],
) -> Iter["ReasonedHighlight"]:
    pipeline = pipelinename2pipeline[pipeline_name]
    prompts = await pipeline(Iter(highlights))
    return prompts


async def run_pipelines(
    pairs: Iter["HighlightWithPipeline"],
) -> Iter["ReasonedHighlight"]:
    pipelinename2pipeline = {pair.pipeline.name: pair.pipeline for pair in pairs}
    pipelines_with_highlights = pairs.groupby(lambda _: _.pipeline.name)

    examples: Sequence[ReasonedHighlight] = []
    for pipeline_name, pairs_instance in pipelines_with_highlights:
        logging.info(f"Running pipeline {pipeline_name}")
        for pair in pairs_instance:
            examples.extend(
                await run_pipeline(
                    pipeline_name=pipeline_name,
                    pipelinename2pipeline=pipelinename2pipeline,
                    highlights=[pair.highlight],
                )
            )

    return Iter(examples)
