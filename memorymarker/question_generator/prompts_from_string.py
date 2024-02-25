import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain.schema.output import LLMResult


def lowercase_keys(d: dict[str, str]) -> dict[str, str]:
    return {k.lower(): v for k, v in d.items()}


def prompts_from_string(text: str) -> dict[str, str]:
    start = text.find("{")
    end = text.rfind("}") + 1
    return lowercase_keys(ast.literal_eval(text[start:end]))  # type: ignore


def llmresult_to_qas(output: "LLMResult") -> list[dict[str, str]]:
    return [prompts_from_string(response[0].text) for response in output.generations]
