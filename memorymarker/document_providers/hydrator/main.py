import re
from typing import TYPE_CHECKING, Callable, Sequence
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from joblib import Memory

from memorymarker.document_providers.ContextualizedHighlight import (
    ContextualizedHighlight,
)

if TYPE_CHECKING:
    from memorymarker.document_providers.base import OrphanHighlight

memory = Memory(".soup_download_cache", verbose=0)


@memory.cache()  # type: ignore
def download_soup_from_url(url: str) -> BeautifulSoup:
    # Send HTTP request to URL and save the response from server in a response object called r
    r = requests.get(url)

    # Create a BeautifulSoup object and specify the parser
    soup = BeautifulSoup(r.text, "html.parser")
    return soup


class ContextParser:
    @staticmethod
    def get_highlight_context(
        soup: BeautifulSoup,
        highlight: str,
        n_chars_before: int = 100,
        n_chars_after: int = 100,
    ) -> str:
        highlight_selection = soup.find(text=re.compile(highlight))

        if highlight_selection is None:
            print(f"Could not find highlight {highlight} in {soup.title}")
            return ""

        highlight_container: Tag = highlight_selection.parent.parent  # type: ignore

        context_strings: list[str] = []

        for child in highlight_container.descendants:
            if isinstance(child, NavigableString):
                context_strings.append(str(child))

        context = " ".join(context_strings)

        context = ContextParser._select_context_slice(
            highlight=highlight,
            n_chars_before=n_chars_before,
            n_chars_after=n_chars_after,
            context=context,
        )
        return context

    @staticmethod
    def _select_context_slice(
        highlight: str, n_chars_before: int, n_chars_after: int, context: str
    ) -> str:
        highlight_index = context.find(highlight)
        context_start_index = max(0, highlight_index - n_chars_before)
        context_end_index = min(
            len(context), highlight_index + len(highlight) + n_chars_after
        )

        return context[context_start_index:context_end_index]


class HighlightHydrator:
    def __init__(self, soup_downloader: Callable[[str], BeautifulSoup]) -> None:
        self.soup_downloader = soup_downloader

    def hydrate_highlights(
        self, highlights: Sequence["OrphanHighlight"]
    ) -> Sequence[ContextualizedHighlight | None]:
        hydrated_highlights: list[ContextualizedHighlight | None] = []
        for highlight in highlights:
            try:
                page = urlopen(highlight.uri)
            except Exception:
                print(f"Could not open {highlight.uri}")
                hydrated_highlights.append(None)
                continue

            soup = self.soup_downloader(page)
            context = ContextParser.get_highlight_context(
                soup=soup, highlight=highlight.highlight
            )
            hydrated_highlights.append(
                ContextualizedHighlight(
                    highlighted_text=highlight.highlight,
                    source_doc_uri=highlight.uri,
                    source_doc_title=highlight.title,
                    prefix=context[:100],
                    suffix=context[-100:],
                )  # type: ignore
            )

        return hydrated_highlights


if __name__ == "__main__":
    result = download_soup_from_url(
        "https://www.gutenberg.org/files/2701/2701-h/2701-h.htm"
    )
