import asyncio
import datetime as dt
from dataclasses import dataclass
from typing import Mapping, Sequence

import pytz
from bs4 import BeautifulSoup

from memorymarker.data_access.highlight_sources.base import HydratedHighlight
from memorymarker.data_access.highlight_sources.hypothesis import (
    HypothesisHighlightGetter,
)
from memorymarker.data_access.hydrator.main import HighlightHydrator
from memorymarker.data_access.persist_questions.markdown import write_qa_prompt_to_md
from memorymarker.domain.highlights_to_questions import (
    highlights_to_questions,
    initialize_model,
)

if __name__ == "__main__":
    print("Getting highlights")
    highlights = HypothesisHighlightGetter(username="ryqiem").get_highlights_since_date(
        dt.datetime.now(tz=pytz.UTC) - dt.timedelta(days=200),
    )
    print("Hydrating highlights")
    hydrated_highlights = HighlightHydrator(
        soup_downloader=BeautifulSoup,
    ).hydrate_highlights(highlights=highlights)

    highlights_with_context: list[HydratedHighlight] = [
        h for h in hydrated_highlights if h is not None
    ]

    print("Generating QAs")
    model = initialize_model(model_name="gpt-4")
    questions = asyncio.run(
        highlights_to_questions(model=model, highlights=list(highlights_with_context)),
    )

    print("Saving to disk")
    [write_qa_prompt_to_md(q) for q in questions]
