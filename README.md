# Web Search — Mini Search Engine (Crawl + Inverted Index)

## 1. Project Overview

This project is a **small end-to-end search tool**: it **crawls** a public quotes website, **builds an inverted index** over the crawled text, **persists** that index to disk, and **searches** it from an interactive CLI. It is intended as a teaching/demo pipeline (crawler → indexer → retriever), not a production web search engine.

**Data source:** [Quotes to Scrape](https://quotes.toscrape.com/) — paginated HTML pages; each page contributes quote text and author names to the indexed corpus.

---

## 2. Features

| Area | What it does |
|------|----------------|
| **Crawler** (`src/crawler.py`) | Fetches pages, parses HTML with BeautifulSoup, follows “next” links, extracts quote + author strings per page. |
| **Inverted index** (`src/indexer.py`) | Tokenizes text, maps **term → { URL → posting }** with **frequency** and **word positions** in the document token stream. |
| **Multi-word search** (`src/search.py`) | **`find`** treats the query as multiple terms joined by **AND** (only URLs containing **every** term are returned), then ranks by a simple score (sum of term frequencies on that URL). |
| **Save / load** | **`build`** writes `data/index.json`; **`load`** reads it back so you can search without re-crawling. |

---

## 3. Project Structure

```
web-search/
├── README.md
├── requirements.txt
├── data/                 # created after `build`; holds index.json (gitignored in real submissions if needed)
├── src/
│   ├── main.py           # REPL: build / load / print / find
│   ├── crawler.py        # HTTP fetch + HTML extraction
│   ├── indexer.py        # tokenize, build index, JSON save/load
│   └── search.py         # print_word, find_pages (AND + ranking)
└── tests/
    ├── test_crawler.py
    ├── test_indexer.py
    └── test_search.py
```

---

## 4. Installation

From the **repository root**:

```bash
pip install -r requirements.txt
```

**Requirements:** Python 3.6+ recommended (matches the test toolchain used in this repo). Network access is required for a real `build` run.

---

## 5. Usage (CLI)

The REPL is started from **`src/`** because `main.py` uses **plain imports** (`from crawler import …`), not a package name:

```bash
cd src
python main.py
```

Then type commands at the `>` prompt (input is normalized to **lowercase** in code, so `Build` and `build` behave the same).

| Command | Example | Behavior |
|---------|---------|----------|
| **`build`** | `build` | Crawl the site → build inverted index → save to **`data/index.json`**. |
| **`load`** | `load` | Load **`data/index.json`** into memory. Use this after a previous `build`, or to avoid re-crawling. |
| **`print <word>`** | `print change` | Show the inverted-list entry for a **single** token: per-URL **frequency** and **positions**. |
| **`find <word1> <word2> …`** | `find good friends` | **Multi-word AND search:** only pages that contain **all** listed terms; results printed with a simple relevance **score**. |
| **Exit** | `exit` or `quit` | Leave the REPL. |

**Important for demos / grading:**

- **`print`** is implemented as `command.split(" ")[1]` — use **one word** after `print` (e.g. `print friends`), not a phrase.
- **`find`** takes everything after `find` as the query string; spaces separate terms (e.g. `find word1 word2`).
- The crawler sleeps **6 seconds** between page requests (politeness). A full site `build` is slow by design.

If you run `print` or `find` before **`build`** or **`load`**, the program reminds you that the index is not in memory.

---

## 6. Testing

From the **repository root** (not `src/`):

```bash
pytest
```

Useful variants:

```bash
pytest -v                 # verbose test names
pytest tests/test_search.py   # single file
pytest --cov=src --cov-report=term-missing   # coverage (pytest-cov in requirements)
```

Tests append `src/` to `sys.path` so modules import as `crawler`, `indexer`, `search` without installing a package. Crawler tests **mock** `requests.get` and **patch** `time.sleep` so the suite does not hit the network or wait real seconds.

---

## 7. Design Decisions

**Why an inverted index?**  
Storing `word → list of (document, stats)` makes **per-term lookup O(1)** in the vocabulary map instead of scanning every page for every query. That is the standard IR structure for this scale of assignment.

**Why AND for multi-word `find`?**  
Requiring **all** query terms to appear **narrows** the result set and matches the usual “every keyword must match” interpretation for a minimal CLI demo. OR or ranked free-text would need different UX and scoring rules.

**Why store `frequency` and `positions`?**  
- **`frequency`** is used **today** for ranking: `find_pages` sums each term’s frequency on a URL and sorts descending (`search.py`).  
- **`positions`** are the indices of tokens in the **flattened word sequence** of each page. They are the right hook for **future** improvements (phrase search, proximity windows, snippets) without changing the on-disk JSON shape again.

**Why JSON on disk?**  
Human-readable, easy to inspect for debugging, and sufficient for homework-sized indexes; a binary format would be faster but harder to mark and explain on video.

---

## 8. AI Usage (transparency)

I used an **AI coding assistant** (e.g. Cursor) during parts of this project. Below is a **concrete** account, not a generic “AI helped a lot” statement.

**What the AI helped with**

- **Scaffolding** for `pytest`: `@patch("crawler.requests.get")`, `Mock` response objects, and table-style tests for `find_pages` / `print_word` against a **small fake index** instead of live HTTP.  
- **Initial README structure** and wording for install/run commands; I then aligned it with the **actual** REPL parsing (`print` single token, `find` strip after `find`).  
- **Boilerplate** for the inverted-index nested dict (`word → url → {frequency, positions}`) consistent with the docstring in `indexer.py`.

**Where the AI was wrong or risky**

- **Run directory:** suggestions often assume `python -m src.main` or a `setup.py` install; this repo expects **`cd src` + `python main.py`**. Running from the repo root breaks imports unless `PYTHONPATH` is set.  
- **DOM assumptions:** any selector for `quotes.toscrape.com` must be checked against **real HTML**; generated selectors can drift if the site template changes.  
- **Edge cases:** e.g. `print` with multiple tokens — the current `split(" ")[1]` behavior is easy to miss in a quick AI review.

**How I changed or verified the work**

- Ran **`pytest`** from the project root until all tests passed; fixed anything that failed (paths, mocks, expectations).  
- Manually traced **`main.py`** input flow (`strip().lower()`, `find` substring) so the README **matches the code** the instructor will run.  
- Confirmed crawler politeness (`time.sleep(6)`) and **BASE_URL** in `crawler.py` against the assignment’s target site.

If you extend the project, re-run tests after any AI-suggested refactor and **re-check** `build` once on a real network when deadlines allow.

---

## 9. Ethics / crawling note

Use [quotes.toscrape.com](https://quotes.toscrape.com/) only in a **reasonable** way: the built-in delay is there to reduce load. Do not point the crawler at sites you do not have permission to stress-test.
