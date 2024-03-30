from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import pydantic

    from memorymarker.question_generator.completers.openai_completer import (
        ModelCompleter,
    )
    from memorymarker.question_generator.reasoned_highlight import ReasonedHighlight


class FlowStep(Protocol):
    def __hash__(self) -> int:
        ...

    async def __call__(self, highlight: "ReasonedHighlight") -> "ReasonedHighlight":
        ...


class ResponseModelStep:
    model_completer: "ModelCompleter"

    async def __call__(self, highlight: "ReasonedHighlight") -> "pydantic.BaseModel":
        ...
