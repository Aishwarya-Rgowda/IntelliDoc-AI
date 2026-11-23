import re
from collections import Counter
from functools import lru_cache

from app.config import ENABLE_SEMANTIC_SEARCH

STOP_WORDS = {
    "the", "and", "for", "that", "with", "this", "from", "are", "was", "were",
    "what", "when", "where", "which", "who", "how", "why", "you", "your",
    "into", "about", "have", "has", "had", "not", "but", "can", "will", "does", "did",
}


def terms(text: str) -> list[str]:
    return [word for word in re.findall(r"[a-zA-Z0-9]{2,}", text.lower()) if word not in STOP_WORDS]


def _paragraphs(documents):
    rows = []
    for doc in documents:
        parts = [part.strip() for part in re.split(r"\n+|(?<=[.!?])\s+", doc.extracted_text or "") if len(part.strip()) > 25]
        rows.extend((doc, part) for part in parts)
    return rows


@lru_cache(maxsize=1)
def _embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def _semantic_scores(question: str, passages: list[str]) -> list[float] | None:
    if not ENABLE_SEMANTIC_SEARCH or not passages:
        return None
    try:
        model = _embedding_model()
        vectors = model.encode([question, *passages], normalize_embeddings=True)
        query_vector = vectors[0]
        return [float(query_vector @ vector) for vector in vectors[1:]]
    except (ImportError, OSError, RuntimeError):
        # Optional model/dependency unavailable: use deterministic lexical retrieval.
        return None


def answer_question(question: str, documents, limit: int = 4) -> tuple[str, list[dict]]:
    query_terms = set(terms(question))
    if not query_terms:
        return "Please ask a question containing meaningful keywords.", []

    rows = _paragraphs(documents)
    passages = [paragraph for _, paragraph in rows]
    semantic_scores = _semantic_scores(question, passages)

    ranked = []
    for index, (doc, paragraph) in enumerate(rows):
        if semantic_scores is not None:
            score = semantic_scores[index]
        else:
            words = terms(paragraph)
            if not words:
                continue
            counts = Counter(words)
            overlap = sum(counts[word] for word in query_terms)
            coverage = len(query_terms.intersection(counts)) / len(query_terms)
            score = overlap * (0.5 + coverage)
        if score > 0:
            ranked.append((score, doc, paragraph))

    ranked.sort(key=lambda item: item[0], reverse=True)
    selected = ranked[:limit]
    if not selected:
        return "I couldn't find a relevant passage in your uploaded documents. Try rephrasing the question or uploading a document containing the topic.", []

    answer = "Here are the most relevant passages I found in your documents:\n\n" + "\n\n".join(
        f"{index}. {paragraph}" for index, (_, _, paragraph) in enumerate(selected, 1)
    )
    sources = [
        {"document_id": doc.id, "filename": doc.filename, "relevance_score": round(float(score), 3)}
        for score, doc, _ in selected
    ]
    return answer, sources
