from types import SimpleNamespace

from app.services.retrieval import answer_question


def test_retrieval_returns_matching_passage_and_source():
    document = SimpleNamespace(
        id=7,
        filename="network-security.txt",
        extracted_text="\n".join([
            "Network security protects computer systems and data from unauthorized access.",
            "A database index helps speed up searches in large tables.",
        ]),
    )

    answer, sources = answer_question("What protects systems from unauthorized access?", [document])

    assert "Network security protects computer systems" in answer
    assert sources
    assert sources[0]["document_id"] == 7
    assert sources[0]["filename"] == "network-security.txt"


def test_retrieval_handles_no_matching_passage():
    document = SimpleNamespace(id=3, filename="notes.txt", extracted_text="Cooking pasta requires boiling water.")

    answer, sources = answer_question("Explain cryptographic certificates", [document])

    assert "couldn't find a relevant passage" in answer
    assert sources == []


def test_retrieval_handles_empty_question_terms():
    answer, sources = answer_question("!!!", [])

    assert "meaningful keywords" in answer
    assert sources == []
