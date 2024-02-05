from dotenv import load_dotenv

from .omnivore import Omnivore

load_dotenv()


def test_omnivore():
    highlights = Omnivore().get_documents()
    assert highlights.count() > 0
