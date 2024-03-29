from dataclasses import dataclass
from typing import Mapping

from iterpy.iter import Iter
from omnivoreql import OmnivoreQL

from memorymarker.document_providers.Document import OmnivoreDocument

from .base import DocumentProvider


@dataclass
class Omnivore(DocumentProvider):
    api_key: str

    def __post_init__(self):
        self.client = OmnivoreQL(self.api_key)

    def _parse_doc(self, document: Mapping[str, str]) -> OmnivoreDocument:
        return OmnivoreDocument(
            title=document["title"],
            uri=document["url"],
            highlights=document["highlights"],  # type: ignore
            slug=document["slug"],
        )

    def get_documents(self) -> Iter[OmnivoreDocument]:
        documents = (
            Iter(self.client.get_articles(limit=1000)["search"]["edges"])
            .map(lambda a: a["node"])
            .map(self._parse_doc)
            .flatten()
        )
        return documents
