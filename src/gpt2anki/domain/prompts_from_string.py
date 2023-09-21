import ast

from langchain.schema.output import LLMResult


def prompts_from_string(text: str) -> dict[str, str]:
    start = text.find("{")
    end = text.rfind("}") + 1
    return ast.literal_eval(text[start:end])


def llmresult_to_qas(output: LLMResult) -> list[dict[str, str]]:
    return [prompts_from_string(response[0].text) for response in output.generations]
