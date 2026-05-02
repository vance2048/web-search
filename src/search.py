# src/search.py

def print_word(index, word):
    """
    Print inverted index for a specific word.
    """

    if index is None:
        print("Index not loaded. Please run 'build' or 'load' first.")
        return

    word = word.lower()

    if word not in index:
        print(f"Word '{word}' not found in index.")
        return

    print(f"\nInverted index for '{word}':\n")

    for url, data in index[word].items():
        freq = data["frequency"]
        positions = data["positions"]

        print(f"Page: {url}")
        print(f"  Frequency: {freq}")
        print(f"  Positions: {positions}")
        print()