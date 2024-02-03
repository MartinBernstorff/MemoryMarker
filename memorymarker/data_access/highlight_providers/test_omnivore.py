import datetime

from dotenv import load_dotenv

from .omnivore import Omnivore

load_dotenv()


def test_omnivore():
    highlights = Omnivore().get_highlights_since_date(
        datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
    )
    assert len(highlights) > 0