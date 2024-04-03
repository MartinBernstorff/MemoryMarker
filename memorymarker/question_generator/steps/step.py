from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import pydantic

    from memorymarker.question_generator.completers.openai_completer import (
        ModelCompleter,
    )
    from memorymarker.question_generator.reasoned_highlight import Highlights


class FlowStep(Protocol):
    def identity(self) -> str:
        ...

    async def __call__(self, highlight: "Highlights") -> "Highlights":
        ...


class ResponseModelStep:
    model_completer: "ModelCompleter"

    async def __call__(self, highlight: "Highlights") -> "pydantic.BaseModel":
        ...
