from types import SimpleNamespace

from app.services.duplicates import find_duplicates, fingerprint, similarity


def document(doc_id, filename, text):
    return SimpleNamespace(id=doc_id, filename=filename, extracted_text=text)


def test_exact_duplicate_detected_even_with_formatting_changes():
    docs = [
        document(1, "first.txt", "Hello, WORLD!\nThis is a document."),
        document(2, "copy.txt", "hello world this is a document"),
    ]

    matches = find_duplicates(docs)

    assert len(matches) == 1
    assert matches[0]["match_type"] == "exact"
    assert matches[0]["similarity"] == 1.0


def test_near_duplicate_detected():
    first = " ".join(["alpha beta gamma delta epsilon"] * 10)
    second = first + " additional words at the end"
    assert similarity(first, second) >= 0.85


def test_unrelated_documents_are_not_reported():
    docs = [
        document(1, "one.txt", "apple orange banana fruit"),
        document(2, "two.txt", "database transaction isolation concurrency"),
    ]
    assert find_duplicates(docs) == []


def test_fingerprint_is_stable_after_normalization():
    assert fingerprint("Hello, World!") == fingerprint("hello world")
