# src/search.py
import re

def tokenize_query(query):
    """
    Tokenize query and make it case-insensitive.
    """
    return re.findall(r"\b\w+\b", query.lower())


def find_pages(index, query):
    """
    Find pages that contain all query words.
    Example:
        find good friends
    means:
        return pages containing both 'good' and 'friends'
    """

    if index is None:
        print("Index not loaded. Please run 'build' or 'load' first.")
        return []

    query_words = tokenize_query(query)

    if not query_words:
        print("Empty query. Please enter at least one search term.")
        return []

    # 如果某个词不在 index 里，直接无结果
    for word in query_words:
        if word not in index:
            print("No results found.")
            return []

    # 取每个词出现过的页面集合
    page_sets = []

    for word in query_words:
        pages = set(index[word].keys())
        page_sets.append(pages)

    # AND 查询：求交集
    result_pages = set.intersection(*page_sets)

    if not result_pages:
        print("No results found.")
        return []

    # 简单排序：按所有查询词在页面中的总频率，从高到低
    def score_page(url):
        score = 0
        for word in query_words:
            score += index[word][url]["frequency"]
        return score

    ranked_pages = sorted(result_pages, key=score_page, reverse=True)

    print(f"Found {len(ranked_pages)} page(s):")

    for url in ranked_pages:
        score = score_page(url)
        print(f"- {url}  (score: {score})")
    
    return ranked_pages
        
def print_word(index, word):
    """
    Print inverted index for a specific word.
    """

    if index is None:
        print("Index not loaded. Please run 'build' or 'load' first.")
        return []

    word = word.lower()

    if word not in index:
        print(f"Word '{word}' not found in index.")
        return None

    print(f"\nInverted index for '{word}':\n")

    for url, data in index[word].items():
        freq = data["frequency"]
        positions = data["positions"]

        print(f"Page: {url}")
        print(f"  Frequency: {freq}")
        print(f"  Positions: {positions}")
        print()
        
    return index[word]