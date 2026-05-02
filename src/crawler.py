# src/crawler.py

import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com/"


def crawl_site():
    """
    Crawl all quote pages from quotes.toscrape.com.
    Returns:
        pages: dict {url: text_content}
    """
    pages = {}
    next_url = BASE_URL

    while next_url:
        print(f"Crawling: {next_url}")

        try:
            response = requests.get(next_url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Request failed: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract visible text from quotes
        quotes = soup.find_all("div", class_="quote")
        page_text = []

        for quote in quotes:
            text = quote.find("span", class_="text")
            author = quote.find("small", class_="author")

            if text:
                page_text.append(text.get_text(" ", strip=True))
            if author:
                page_text.append(author.get_text(" ", strip=True))

        pages[next_url] = " ".join(page_text)

        # Find next page
        next_button = soup.find("li", class_="next")
        if next_button:
            next_link = next_button.find("a")
            next_url = urljoin(BASE_URL, next_link["href"])
            time.sleep(6)  # politeness window
        else:
            next_url = None

    return pages