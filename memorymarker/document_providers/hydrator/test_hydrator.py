from bs4 import BeautifulSoup

from memorymarker.document_providers.hydrator.main import ContextParser


def test_context_parser():
    input_soup = BeautifulSoup(
        """
    <html>
        <body>
            <p>Some text</p>
            <p>Some more text</p>
            <p>Even more text</p>
        </body>
    </html>
    """,
        "html.parser",
    )

    expected_output = "\n Some text \n Some more text \n Even more text \n"
    context = ContextParser.get_highlight_context(soup=input_soup, highlight="more")
    assert context == expected_output


def test_context_slicing():
    highlight = "highlight"
    context = "54321highlight12345"

    assert (
        ContextParser._select_context_slice(  # type: ignore
            highlight=highlight, n_chars_before=1, n_chars_after=1, context=context
        )
        == "1highlight1"
    )
