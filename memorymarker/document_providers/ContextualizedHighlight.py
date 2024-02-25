import datetime as dt  # noqa: TCH003

from pydantic import BaseModel


class ContextualizedHighlight(BaseModel):
    source_doc_title: str
    source_doc_uri: str

    prefix: str | None
    highlighted_text: str
    suffix: str | None

    source_highlight_uri: str | None = None
    updated_at: dt.datetime

    @property
    def context(self) -> str:
        context = ""
        context += self.prefix or ""
        context += self.highlighted_text
        context += self.suffix or ""

        return context
