import re
from collections import Counter

from app.services.retrieval import terms


def summarize_text(text: str, max_sentences: int = 5) -> tuple[str, int, int]:
    """Create a concise extractive summary by ranking sentences by term importance."""
    sentences = [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+|\n+", text or "")
        if len(part.strip()) > 20
    ]
    original_words = len((text or "").split())
    if not sentences:
        return "", original_words, 0

    all_terms = terms(text)
    frequencies = Counter(all_terms)
    if not frequencies:
        chosen = sentences[:max_sentences]
    else:
        max_frequency = max(frequencies.values())
        scored = []
        for index, sentence in enumerate(sentences):
            sentence_terms = terms(sentence)
            score = sum(frequencies[word] / max_frequency for word in sentence_terms)
            scored.append((score, index, sentence))
        selected = sorted(scored, key=lambda item: (-item[0], item[1]))[:max_sentences]
        chosen = [sentence for _, _, sentence in sorted(selected, key=lambda item: item[1])]

    summary = " ".join(chosen)
    return summary, original_words, len(summary.split())
