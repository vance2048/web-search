# src/indexer.py

import re
import json
import os


def tokenize(text):
    """
    Convert text to lowercase words.
    """
    return re.findall(r"\b\w+\b", text.lower())


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

    for url, text in pages.items():
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