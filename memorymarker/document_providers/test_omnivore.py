import os

import pytest

from .omnivore import Omnivore


@pytest.fixture(scope="module")
def omnivore_api_key() -> str:
    omnivore_api_key = os.getenv("OMNIVORE_API_KEY")
    if not omnivore_api_key:
        raise ValueError("OMNIVORE_API_KEY environment variable not set")

    return omnivore_api_key


def test_omnivore(omnivore_api_key: str):
    highlights = Omnivore(omnivore_api_key).get_documents()
    assert highlights.count() > 0
