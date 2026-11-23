import hashlib
import re


def normalize_text(text: str) -> str:
    """Normalize extracted text so formatting differences do not hide duplicates."""
    return " ".join(re.findall(r"\w+", (text or "").casefold()))


def fingerprint(text: str) -> str:
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _shingles(text: str, size: int = 5) -> set[tuple[str, ...]]:
    words = normalize_text(text).split()
    if not words:
        return set()
    if len(words) < size:
        return {tuple(words)}
    return {tuple(words[index:index + size]) for index in range(len(words) - size + 1)}


def similarity(first: str, second: str) -> float:
    """Return shingle Jaccard similarity (0..1), a lightweight near-duplicate signal."""
    left, right = _shingles(first), _shingles(second)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def find_duplicates(documents, threshold: float = 0.85) -> list[dict]:
    """Find exact and near duplicates within one already owner-scoped document list."""
    matches = []
    for index, first in enumerate(documents):
        for second in documents[index + 1:]:
            score = similarity(first.extracted_text, second.extracted_text)
            if score >= threshold:
                matches.append({
                    "first_document_id": first.id,
                    "first_filename": first.filename,
                    "second_document_id": second.id,
                    "second_filename": second.filename,
                    "similarity": round(score, 4),
                    "match_type": "exact" if fingerprint(first.extracted_text) == fingerprint(second.extracted_text) else "near",
                })
    return matches
