import re
from collections import Counter
from app.models import Document

STOP_WORDS = {"the","and","for","that","with","this","from","are","was","were","what","when","where","which","who","how","why","you","your","into","about","have","has","had","not","but","can","will","does","did"}

def terms(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z0-9]{2,}", text.lower()) if w not in STOP_WORDS]

def answer_question(question: str, documents: list[Document], limit: int = 4) -> tuple[str, list[dict]]:
    query_terms = set(terms(question))
    if not query_terms:
        return "Please ask a question containing meaningful keywords.", []
    ranked = []
    for doc in documents:
        paragraphs = [p.strip() for p in re.split(r"\n+|(?<=[.!?])\s+", doc.extracted_text) if len(p.strip()) > 25]
        for paragraph in paragraphs:
            words = terms(paragraph)
            if not words:
                continue
            counts = Counter(words)
            overlap = sum(counts[t] for t in query_terms)
            coverage = len(query_terms.intersection(counts)) / len(query_terms)
            score = overlap * (0.5 + coverage)
            if score:
                ranked.append((score, doc, paragraph))
    ranked.sort(key=lambda item: item[0], reverse=True)
    selected = ranked[:limit]
    if not selected:
        return "I couldn't find a relevant passage in your uploaded documents. Try rephrasing the question or uploading a document containing the topic.", []
    answer = "Here are the most relevant passages I found in your documents:\n\n" + "\n\n".join(f"{i}. {p}" for i, (_, _, p) in enumerate(selected, 1))
    sources = [{"document_id": d.id, "filename": d.filename, "relevance_score": round(float(s), 2)} for s, d, _ in selected]
    return answer, sources
