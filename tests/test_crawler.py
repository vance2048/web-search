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
            <h1>Quotes to Scrape</h1>
            <div class="tags-box">
                <a class="tag" href="/tag/love/">love</a>
            </div>
            <div class="quote">
                <span class="text">“Good friends are important.”</span>
                <small class="author">Test Author</small>
                <div class="tags">
                    <a class="tag" href="/tag/friends/">friends</a>
                    <a class="tag" href="/tag/good/">good</a>
                </div>
            </div>
        </body>
    </html>
    """

    mock_get.return_value = mock_response(html)

    pages = crawl_site()

    assert len(pages) == 4
    assert "https://quotes.toscrape.com/" in pages
    assert "https://quotes.toscrape.com/tag/love/" in pages
    assert "https://quotes.toscrape.com/tag/friends/" in pages
    assert "https://quotes.toscrape.com/tag/good/" in pages
    data = pages["https://quotes.toscrape.com/"]
    assert data["title"] == "Quotes to Scrape"
    assert data["top_tags"] == ["love"]
    assert len(data["quotes"]) == 1
    assert "Good friends are important" in data["quotes"][0]["text"]
    assert data["quotes"][0]["author"] == "Test Author"
    assert data["quotes"][0]["tags"] == ["friends", "good"]


@patch("crawler.time.sleep", return_value=None)
@patch("crawler.requests.get")
def test_tag_href_with_page_segment_enqueues_tag_root(mock_get, mock_sleep):
    """Site uses /tag/slug/page/1/ on quote links; crawler must still open /tag/slug/."""
    home = """
    <html><body>
        <h1>Quotes to Scrape</h1>
        <div class="quote">
            <span class="text">“Hi.”</span>
            <small class="author">A</small>
            <div class="tags">
                <a class="tag" href="/tag/be-yourself/page/1/">be-yourself</a>
            </div>
        </div>
    </body></html>
    """
    tag_hub = """
    <html><body><h1>Quotes to Scrape</h1></body></html>
    """
    mock_get.side_effect = [mock_response(home), mock_response(tag_hub)]

    pages = crawl_site()

    assert "https://quotes.toscrape.com/" in pages
    assert "https://quotes.toscrape.com/tag/be-yourself/" in pages


@patch("crawler.time.sleep", return_value=None)
@patch("crawler.requests.get")
def test_crawl_multiple_pages(mock_get, mock_sleep):
    page1 = """
    <html>
        <body>
            <h1>Quotes to Scrape</h1>
            <div class="quote">
                <span class="text">“Page one quote.”</span>
                <small class="author">Author One</small>
                <div class="tags"><a class="tag" href="/tag/a/">a</a></div>
            </div>
            <li class="next"><a href="/page/2/">Next</a></li>
        </body>
    </html>
    """

    page2 = """
    <html>
        <body>
            <h1>Quotes to Scrape</h1>
            <div class="quote">
                <span class="text">“Page two quote.”</span>
                <small class="author">Author Two</small>
                <div class="tags"><a class="tag" href="/tag/b/">b</a></div>
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
    p1 = pages["https://quotes.toscrape.com/"]
    p2 = pages["https://quotes.toscrape.com/page/2/"]
    assert "Page one quote" in p1["quotes"][0]["text"]
    assert p1["quotes"][0]["author"] == "Author One"
    assert p1["quotes"][0]["tags"] == ["a"]
    assert "Page two quote" in p2["quotes"][0]["text"]
    assert p2["quotes"][0]["author"] == "Author Two"
    assert p2["quotes"][0]["tags"] == ["b"]


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


@patch("crawler.time.sleep", return_value=None)
@patch("crawler.requests.get")
def test_crawl_author_page_from_about_link(mock_get, mock_sleep):
    home = """
    <html><body>
        <h1>Quotes to Scrape</h1>
        <div class="quote">
            <span class="text">“Hello.”</span>
            <small class="author">Albert Einstein</small>
            <a href="/author/Albert-Einstein">(about)</a>
        </div>
    </body></html>
    """
    author = """
    <html><body>
        <h1><a href="/">Quotes to Scrape</a></h1>
        <div class="author-details">
            <h3 class="author-title">Albert Einstein</h3>
            <p><strong>Born:</strong>
               <span class="author-born-date">March 14, 1879</span>
               <span class="author-born-location">in Ulm, Germany</span></p>
            <div class="author-description">Physicist.</div>
        </div>
    </body></html>
    """
    mock_get.side_effect = [mock_response(home), mock_response(author)]

    pages = crawl_site()

    assert len(pages) == 2
    assert "https://quotes.toscrape.com/" in pages
    assert "https://quotes.toscrape.com/author/Albert-Einstein/" in pages
    bio = pages["https://quotes.toscrape.com/author/Albert-Einstein/"]
    assert bio["author_profile"]["name"] == "Albert Einstein"
    assert bio["author_profile"]["born_date"] == "March 14, 1879"
    assert "Ulm" in bio["author_profile"]["born_location"]
    assert "Physicist" in bio["author_profile"]["description"]