from typing import TYPE_CHECKING, Sequence

from iterpy.iter import Iter

if TYPE_CHECKING:
    from memorymarker.question_generator_v2.main import HighlightWithPipeline
    from memorymarker.question_generator_v2.reasoned_highlight import ReasonedHighlight


def run_pipelines(
    pairs: "Iter[HighlightWithPipeline]",
) -> Sequence["ReasonedHighlight"]:
    pipelinename2pipeline = {pair.pipeline.name: pair.pipeline for pair in pairs}

    pipelines_with_highlights = pairs.groupby(lambda _: _.pipeline.name)

    examples: Sequence[ReasonedHighlight] = []
    for pipeline_name, pair in pipelines_with_highlights:
        print(f"Creating examples for {pipeline_name}")
        highlights = [pair.highlight for pair in pair]
        pipeline = pipelinename2pipeline[pipeline_name]
        prompts = pipeline(Iter(highlights))
        examples.extend(prompts)

    return examples
