# src/main.py

from crawler import crawl_site
from indexer import build_inverted_index, save_index


def build():
    """
    Build command:
    1. Crawl website
    2. Build inverted index
    3. Save index to file
    """
    print("Building index...")

    pages = crawl_site()
    index = build_inverted_index(pages)
    save_index(index)

    print("Build completed successfully.")
    print(f"Total pages crawled: {len(pages)}")
    print(f"Total unique words indexed: {len(index)}")


if __name__ == "__main__":
    command = input("> ").strip().lower()

    if command == "build":
        build()
    else:
        print("Unknown command.")