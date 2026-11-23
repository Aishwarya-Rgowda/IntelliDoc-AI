from types import SimpleNamespace

from app.services.retrieval import answer_question


def test_answer_uses_extracts_when_no_llm_key(monkeypatch):
    monkeypatch.setattr("app.config.OPENAI_API_KEY", "")
    doc = SimpleNamespace(
        id=12,
        filename="security.txt",
        extracted_text="Multi-factor authentication adds another verification step to protect accounts.",
    )

    answer, sources = answer_question("How does authentication protect accounts?", [doc])

    assert "extractive mode" in answer
    assert "[Source 1: security.txt]" in answer
    assert sources[0]["document_id"] == 12


def test_answer_uses_generated_response_when_available(monkeypatch):
    doc = SimpleNamespace(
        id=13,
        filename="privacy.txt",
        extracted_text="Data minimization means collecting only information needed for a purpose.",
    )
    monkeypatch.setattr("app.services.retrieval._generate_grounded_answer", lambda question, selected: "Data minimization limits collection. [Source 1]")
    answer, sources = answer_question("What is data minimization?", [doc])

    assert answer.startswith("Data minimization limits collection")
    assert sources[0]["filename"] == "privacy.txt"
