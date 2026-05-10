# src/indexer.py

import re
import json
import os


def tokenize(text):
    """
    Convert text to lowercase words.
    """
    return re.findall(r"\b\w+\b", text.lower())


def _page_to_index_text(page):
    """
    Flatten crawler page payload (dict) or legacy plain string for indexing.
    """
    if isinstance(page, str):
        return page
    parts = [page.get("title") or ""]
    parts.extend(page.get("top_tags") or [])
    prof = page.get("author_profile")
    if prof:
        parts.append(prof.get("name") or "")
        parts.append(prof.get("born_date") or "")
        parts.append(prof.get("born_location") or "")
        parts.append(prof.get("description") or "")
    for q in page.get("quotes") or []:
        parts.append(q.get("text") or "")
        parts.append(q.get("author") or "")
        parts.extend(q.get("tags") or [])
    return " ".join(p for p in parts if p)


def build_inverted_index(pages):
    """
    Build inverted index.

    Structure:
    {
        "word": {
            "url": {
                "frequency": 3,
                "positions": [0, 5, 12]
            }
        }
    }
    """
    index = {}

    for url, page in pages.items():
        text = _page_to_index_text(page)
        words = tokenize(text)

        for position, word in enumerate(words):
            if word not in index:
                index[word] = {}

            if url not in index[word]:
                index[word][url] = {
                    "frequency": 0,
                    "positions": []
                }

            index[word][url]["frequency"] += 1
            index[word][url]["positions"].append(position)

    return index


def save_index(index, filepath="data/index.json"):
    """
    Save inverted index to file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"Index saved to {filepath}")


def load_index(filepath="data/index.json"):
    """
    Load inverted index from file system.
    """
    if not os.path.exists(filepath):
        print(f"Index file not found: {filepath}")
        print("Please run 'build' first.")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            index = json.load(f)

        print(f"Index loaded from {filepath}")
        print(f"Total unique words: {len(index)}")
        return index

    except json.JSONDecodeError:
        print("Index file is corrupted or not valid JSON.")
        return None