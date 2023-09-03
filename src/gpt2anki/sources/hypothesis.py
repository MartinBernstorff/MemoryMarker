import datetime as dt
import json
import re

import pytz
import requests
from gpt2anki.api_keys import HYPOTHESIS_API_KEY
from gpt2anki.sources.base import HighlightSource, OrphanHighlight
from pydantic import BaseModel


class SearchRequest(BaseModel):
    search_after: dt.datetime
    username: str

    @property
    def url_encoded_date(self) -> str:
        return self.search_after.isoformat()

    @property
    def gmail_address(self) -> str:
        return f"{self.username}@gmail.com"

    @property
    def hypothesis_user_id(self) -> str:
        user_id = f"acct:{self.username}@hypothes.is"

        assert (
            len(re.findall(string=user_id, pattern=r"acct:[A-Za-z0-9._]{3,30}@.*")) == 1
        )
        return user_id


class HypothesisHighlightGetter(HighlightSource):
    def __init__(self, api_key: str, username: str):
        self.api_key: str = api_key
        self.endpoint: str = "https://api.hypothes.is/api/search"
        self.username: str = username

    def get_highlights_since_date(
        self,
        date: dt.datetime,
    ) -> tuple[OrphanHighlight, ...]:
        request_spec = SearchRequest(search_after=date, username=self.username)

        params = {
            "search_after": request_spec.url_encoded_date,
            "user": request_spec.hypothesis_user_id,
            "sort": "created",
            "order": "desc",
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.get(url=self.endpoint, params=params, headers=headers)

        # UTF-8 encode the response content
        content = response.content.decode("utf-8")

        # Convert the response content to a Python dictionary
        response_dict = json.loads(content)

        highlights: list[OrphanHighlight] = []
        errors: list[str] = []
        for row in response_dict["rows"]:
            try:
                highlights.append(
                    OrphanHighlight(
                        highlight=row["target"][0]["selector"][2]["exact"],
                        uri=row["uri"],
                        title=row["document"]["title"][0],
                    ),
                )
            except KeyError:
                errors.append(row)

        print(f"n Errors: {len(errors)}")

        return tuple(highlights)


if __name__ == "__main__":
    # Load api-key from .env file
    api_key = HYPOTHESIS_API_KEY
    response = HypothesisHighlightGetter(
        api_key=api_key,
        username="ryqiem",
    ).get_highlights_since_date(dt.datetime.now(tz=pytz.UTC) - dt.timedelta(days=200))

    pass
