import sys
import os
from unittest.mock import patch, Mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from crawler import crawl_site


def mock_response(html):
    response = Mock()
    response.text = html
    response.raise_for_status = Mock()
    return response


@patch("crawler.time.sleep", return_value=None)
@patch("crawler.requests.get")
def test_crawl_single_page(mock_get, mock_sleep):
    html = """
    <html>
        <body>
            <div class="quote">
                <span class="text">“Good friends are important.”</span>
                <small class="author">Test Author</small>
            </div>
        </body>
    </html>
    """

    mock_get.return_value = mock_response(html)

    pages = crawl_site()

    assert len(pages) == 1
    assert "https://quotes.toscrape.com/" in pages
    assert "Good friends are important" in pages["https://quotes.toscrape.com/"]
    assert "Test Author" in pages["https://quotes.toscrape.com/"]


@patch("crawler.time.sleep", return_value=None)
@patch("crawler.requests.get")
def test_crawl_multiple_pages(mock_get, mock_sleep):
    page1 = """
    <html>
        <body>
            <div class="quote">
                <span class="text">“Page one quote.”</span>
                <small class="author">Author One</small>
            </div>
            <li class="next"><a href="/page/2/">Next</a></li>
        </body>
    </html>
    """

    page2 = """
    <html>
        <body>
            <div class="quote">
                <span class="text">“Page two quote.”</span>
                <small class="author">Author Two</small>
            </div>
        </body>
    </html>
    """

    mock_get.side_effect = [
        mock_response(page1),
        mock_response(page2)
    ]

    pages = crawl_site()

    assert len(pages) == 2
    assert "https://quotes.toscrape.com/" in pages
    assert "https://quotes.toscrape.com/page/2/" in pages
    assert "Page one quote" in pages["https://quotes.toscrape.com/"]
    assert "Page two quote" in pages["https://quotes.toscrape.com/page/2/"]


@patch("crawler.time.sleep", return_value=None)
@patch("crawler.requests.get")
def test_crawl_uses_politeness_window(mock_get, mock_sleep):
    page1 = """
    <html>
        <body>
            <div class="quote">
                <span class="text">“Page one quote.”</span>
            </div>
            <li class="next"><a href="/page/2/">Next</a></li>
        </body>
    </html>
    """

    page2 = """
    <html>
        <body>
            <div class="quote">
                <span class="text">“Page two quote.”</span>
            </div>
        </body>
    </html>
    """

    mock_get.side_effect = [
        mock_response(page1),
        mock_response(page2)
    ]

    crawl_site()

    mock_sleep.assert_called_with(6)


@patch("crawler.requests.get")
def test_crawl_handles_request_error(mock_get):
    mock_get.side_effect = Exception("Network error")

    pages = crawl_site()

    assert pages == {}