from typing import TYPE_CHECKING

import questionary

if TYPE_CHECKING:
    from iterpy.iter import Iter

    from ..document_providers.omnivore_document import OmnivoreDocument


def select_documents(docs: "Iter[OmnivoreDocument]") -> "Iter[OmnivoreDocument]":
    doc_titles = docs.map(lambda d: d.title).to_list()
    selected_doc_names = questionary.checkbox(
        message="Select documents", choices=doc_titles
    ).ask()
    return docs.filter(lambda d: d.title in selected_doc_names)
