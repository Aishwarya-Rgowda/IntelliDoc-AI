import re
from statistics import median


def inspect_documents(documents: list) -> list[dict]:
    """Flag explainable document-quality signals; these are warnings, not accusations."""
    lengths = [len((doc.extracted_text or "").split()) for doc in documents]
    typical = median(lengths) if lengths else 0
    findings = []
    for doc, word_count in zip(documents, lengths):
        text = doc.extracted_text or ""
        flags = []
        if not text.strip():
            flags.append({"code": "empty_text", "severity": "high", "message": "No extracted text is available."})
        elif word_count < 20:
            flags.append({"code": "very_short", "severity": "low", "message": "The extracted text is unusually short."})
        if word_count and typical and word_count > max(1000, typical * 5):
            flags.append({"code": "unusually_long", "severity": "low", "message": "This document is much longer than the library median."})
        if len(text) > 100 and len(set(text)) <= 4:
            flags.append({"code": "low_text_variety", "severity": "medium", "message": "The text contains very few distinct characters; extraction may be corrupted."})
        if re.search(r"(.)\\1{24,}", text):
            flags.append({"code": "repeated_character_run", "severity": "medium", "message": "A long repeated-character sequence was found."})
        if flags:
            findings.append({
                "document_id": doc.id,
                "filename": doc.filename,
                "word_count": word_count,
                "flags": flags,
            })
    return findings
