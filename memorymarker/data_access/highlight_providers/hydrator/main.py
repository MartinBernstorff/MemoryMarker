import re
from typing import Callable, Sequence
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from joblib import Memory

from memorymarker.data_access.highlight_providers.base import (
    HydratedHighlight,
    OrphanHighlight,
)

memory = Memory("cache", verbose=0)


@memory.cache()
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
        highlight: str,
        n_chars_before: int,
        n_chars_after: int,
        context: str,
    ) -> str:
        highlight_index = context.find(highlight)
        context_start_index = max(0, highlight_index - n_chars_before)
        context_end_index = min(
            len(context),
            highlight_index + len(highlight) + n_chars_after,
        )

        return context[context_start_index:context_end_index]


class HighlightHydrator:
    def __init__(self, soup_downloader: Callable[[str], BeautifulSoup]) -> None:
        self.soup_downloader = soup_downloader

    def hydrate_highlights(
        self,
        highlights: Sequence[OrphanHighlight],
    ) -> Sequence[HydratedHighlight | None]:
        hydrated_highlights: list[HydratedHighlight | None] = []
        for highlight in highlights:
            try:
                page = urlopen(highlight.uri)
            except Exception:
                print(f"Could not open {highlight.uri}")
                hydrated_highlights.append(None)
                continue

            soup = self.soup_downloader(page)
            context = ContextParser.get_highlight_context(
                soup=soup,
                highlight=highlight.highlight,
            )
            hydrated_highlights.append(
                HydratedHighlight(
                    highlight=highlight.highlight,
                    uri=highlight.uri,
                    title=highlight.title,
                    context=context,
                ),  # type: ignore
            )

        return hydrated_highlights


if __name__ == "__main__":
    result = download_soup_from_url(
        "https://www.gutenberg.org/files/2701/2701-h/2701-h.htm",
    )
