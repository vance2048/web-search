# src/crawler.py

import re
import time
from collections import deque

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse


BASE_URL = "https://quotes.toscrape.com/"
_TAG_PATH = re.compile(r"^/tag/[^/]+(?:/page/\d+)?/?$")
_AUTHOR_PATH = re.compile(r"^/author/[^/]+(?:/page/\d+)?/?$")
_MAIN_PAGE_PATH = re.compile(r"^/(?:page/\d+)?/?$")
_TAG_SLUG = re.compile(r"^/tag/([^/]+)")


def _parse_quote_blocks(soup):
    """Shared: sidebar top tags + div.quote rows (listings and author pages if present)."""
    top_tags = []
    tags_box = soup.find("div", class_="tags-box")
    if tags_box:
        for a in tags_box.find_all("a", class_="tag"):
            top_tags.append(a.get_text(strip=True))

    quotes = []
    for quote in soup.find_all("div", class_="quote"):
        text_el = quote.find("span", class_="text")
        author_el = quote.find("small", class_="author")
        tags_div = quote.find("div", class_="tags")
        quote_tags = []
        if tags_div:
            for a in tags_div.find_all("a", class_="tag"):
                quote_tags.append(a.get_text(strip=True))

        quotes.append(
            {
                "text": text_el.get_text(" ", strip=True) if text_el else "",
                "author": author_el.get_text(" ", strip=True) if author_el else "",
                "tags": quote_tags,
            }
        )

    return top_tags, quotes


def _parse_author_details_page(soup, author_box):
    """Author bio page (div.author-details): name, birth, description + any quotes."""
    title_el = soup.find("h1")
    title = title_el.get_text(" ", strip=True) if title_el else ""

    name_el = author_box.find("h3", class_="author-title")
    name = name_el.get_text(" ", strip=True) if name_el else ""

    born_date = ""
    born_span = author_box.find("span", class_="author-born-date")
    if born_span:
        born_date = born_span.get_text(" ", strip=True)

    born_location = ""
    loc_span = author_box.find("span", class_="author-born-location")
    if loc_span:
        born_location = loc_span.get_text(" ", strip=True)

    desc_el = author_box.find("div", class_="author-description")
    description = desc_el.get_text(" ", strip=True) if desc_el else ""

    top_tags, quotes = _parse_quote_blocks(soup)

    return {
        "title": title,
        "top_tags": top_tags,
        "quotes": quotes,
        "author_profile": {
            "name": name,
            "born_date": born_date,
            "born_location": born_location,
            "description": description,
        },
    }


def _parse_quote_page(soup):
    """
    Parse one page: quote listings, or an author bio page (author-details).
    """
    author_box = soup.find("div", class_="author-details")
    if author_box:
        return _parse_author_details_page(soup, author_box)

    title_el = soup.find("h1")
    title = title_el.get_text(" ", strip=True) if title_el else ""

    top_tags, quotes = _parse_quote_blocks(soup)

    return {"title": title, "top_tags": top_tags, "quotes": quotes}


def _normalize_site_url(url):
    """Use https and quotes.toscrape.com host so http/https variants dedupe."""
    p = urlparse(url)
    if p.netloc.lower() not in ("quotes.toscrape.com", "www.quotes.toscrape.com"):
        return None
    path = p.path or "/"
    if path != "/" and not path.endswith("/"):
        path = path + "/"
    return urlunparse(("https", "quotes.toscrape.com", path, "", "", ""))


def _tag_listing_root_url(norm):
    """
    Map /tag/slug/ or /tag/slug/page/N/ to canonical https://host/tag/slug/.
    Inline quote links often use .../page/1/; we still need to crawl the tag hub.
    """
    if not norm:
        return None
    path = urlparse(norm).path
    m = _TAG_SLUG.match(path)
    if not m:
        return None
    slug = m.group(1)
    if not slug:
        return None
    root = urlunparse(("https", "quotes.toscrape.com", "/tag/%s/" % slug, "", "", ""))
    return _normalize_site_url(root)


def _is_quote_listing_path(path):
    """Main index, /tag/..., or /author/.../ (and their pagination)."""
    if not path or path == "/":
        return True
    return bool(
        _MAIN_PAGE_PATH.match(path)
        or _TAG_PATH.match(path)
        or _AUTHOR_PATH.match(path)
    )


def _discover_listing_urls(soup, current_url):
    """Pagination 'Next', /tag/name/ hubs, and /author/name/ from each quote's (about) link."""
    found = []
    next_button = soup.find("li", class_="next")
    if next_button:
        link = next_button.find("a", href=True)
        if link:
            found.append(urljoin(current_url, link["href"]))

    for a in soup.find_all("a", class_="tag", href=True):
        href = a["href"]
        if "/tag/" not in href:
            continue
        full = urljoin(current_url, href)
        norm = _normalize_site_url(full)
        if not norm or not _TAG_PATH.match(urlparse(norm).path):
            continue
        root = _tag_listing_root_url(norm)
        if root:
            found.append(root)

    for quote in soup.find_all("div", class_="quote"):
        for a in quote.find_all("a", href=True):
            href = a["href"]
            if "/author/" not in href:
                continue
            full = urljoin(current_url, href)
            path_parts = [p for p in urlparse(full).path.split("/") if p]
            if len(path_parts) >= 3 and path_parts[-1].lower() == "about":
                continue
            norm = _normalize_site_url(full)
            if not norm or not _AUTHOR_PATH.match(urlparse(norm).path):
                continue
            p = urlparse(norm).path.rstrip("/")
            if "/page/" in p:
                continue
            found.append(norm)

    return found


def crawl_site():
    """
    Crawl quote listings: main index (/page/N/), /tag/.../, and author pages
    at /author/.../ (linked from each quote's (about) link).

    Returns:
        pages: dict mapping each page URL to:
            title (str): page heading, e.g. "Quotes to Scrape"
            top_tags (list[str]): sidebar "Top Ten tags" links
            quotes (list[dict]): each with text, author, tags (list[str])
            author_profile (dict, optional): name, born_date, born_location,
                description — only on author detail pages
    """
    pages = {}
    frontier = deque()
    start = _normalize_site_url(BASE_URL)
    frontier.append(start)
    visited = set()

    while frontier:
        raw_url = frontier.popleft()
        next_url = _normalize_site_url(raw_url)
        if not next_url or next_url in visited:
            continue
        path = urlparse(next_url).path
        if not _is_quote_listing_path(path):
            continue
        visited.add(next_url)

        print(f"Crawling: {next_url}")

        try:
            response = requests.get(next_url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Request failed: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        pages[next_url] = _parse_quote_page(soup)

        for href in _discover_listing_urls(soup, next_url):
            child = _normalize_site_url(href)
            if child and child not in visited:
                frontier.append(child)

        if frontier:
            time.sleep(6)  # politeness window

    return pages