from typing import Protocol


class Completer(Protocol):
    def identity(self) -> str:
        ...

    async def __call__(self, prompt: str) -> str:
        ...
