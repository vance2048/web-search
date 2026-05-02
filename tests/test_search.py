import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from search import tokenize_query, find_pages, print_word


def sample_index():
    return {
        "good": {
            "page1": {
                "frequency": 2,
                "positions": [0, 3]
            },
            "page2": {
                "frequency": 1,
                "positions": [1]
            }
        },
        "friends": {
            "page1": {
                "frequency": 1,
                "positions": [2]
            },
            "page3": {
                "frequency": 1,
                "positions": [0]
            }
        },
        "life": {
            "page2": {
                "frequency": 3,
                "positions": [0, 2, 4]
            }
        }
    }


def test_tokenize_query_single_word():
    result = tokenize_query("Good")

    assert result == ["good"]


def test_tokenize_query_multi_word():
    result = tokenize_query("Good Friends")

    assert result == ["good", "friends"]


def test_find_single_word():
    index = sample_index()

    result = find_pages(index, "good")

    assert result == ["page1", "page2"]


def test_find_multi_word_and_query():
    index = sample_index()

    result = find_pages(index, "good friends")

    assert result == ["page1"]


def test_find_non_existing_word():
    index = sample_index()

    result = find_pages(index, "unknown")

    assert result == []


def test_find_empty_query():
    index = sample_index()

    result = find_pages(index, "")

    assert result == []


def test_find_none_index():
    result = find_pages(None, "good")

    assert result == []


def test_find_case_insensitive():
    index = sample_index()

    result = find_pages(index, "GOOD FRIENDS")

    assert result == ["page1"]


def test_print_existing_word():
    index = sample_index()

    result = print_word(index, "good")

    assert result == index["good"]


def test_print_non_existing_word():
    index = sample_index()

    result = print_word(index, "unknown")

    assert result is None