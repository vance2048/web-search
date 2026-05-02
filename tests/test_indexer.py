import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from indexer import tokenize, build_inverted_index, save_index, load_index


def test_tokenize_lowercase():
    text = "Good Friends GOOD"
    result = tokenize(text)

    assert result == ["good", "friends", "good"]


def test_tokenize_removes_punctuation():
    text = "Hello, world! This is good."
    result = tokenize(text)

    assert result == ["hello", "world", "this", "is", "good"]


def test_build_inverted_index_single_page():
    pages = {
        "page1": "good friends good"
    }

    index = build_inverted_index(pages)

    assert index["good"]["page1"]["frequency"] == 2
    assert index["good"]["page1"]["positions"] == [0, 2]
    assert index["friends"]["page1"]["frequency"] == 1
    assert index["friends"]["page1"]["positions"] == [1]


def test_build_inverted_index_multiple_pages():
    pages = {
        "page1": "good friends",
        "page2": "good life"
    }

    index = build_inverted_index(pages)

    assert index["good"]["page1"]["frequency"] == 1
    assert index["good"]["page2"]["frequency"] == 1
    assert index["friends"]["page1"]["positions"] == [1]
    assert index["life"]["page2"]["positions"] == [1]


def test_save_and_load_index(tmpdir):
    index = {
        "good": {
            "page1": {
                "frequency": 2,
                "positions": [0, 2]
            }
        }
    }

    file_path = tmpdir.join("index.json")

    save_index(index, str(file_path))
    loaded_index = load_index(str(file_path))

    assert loaded_index == index


def test_load_missing_file(tmpdir):
    file_path = tmpdir / "missing.json"

    loaded_index = load_index(str(file_path))

    assert loaded_index is None


def test_saved_file_is_valid_json(tmpdir):
    index = {
        "hello": {
            "page1": {
                "frequency": 1,
                "positions": [0]
            }
        }
    }

    file_path = tmpdir.join("index.json")

    save_index(index, str(file_path))

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data == index