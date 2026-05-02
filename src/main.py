# src/main.py

from crawler import crawl_site
from indexer import build_inverted_index, save_index, load_index
from search import print_word, find_pages

index = None

def build():
    global index
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


def load():
    global index

    index = load_index()

    if index is not None:
        print("Load completed successfully.")

if __name__ == "__main__":
    while True:
        command = input("> ").strip().lower()

        if command == "build":
            build()

        elif command == "load":
            load()

        elif command.startswith("print "):
            word = command.split(" ")[1]
            print_word(index, word)

        elif command.lower().startswith("find"):
            query = command[4:].strip()
            find_pages(index, query)

        elif command in ["exit", "quit"]:
            print("Goodbye.")
            break

        else:
            print("Unknown command.")