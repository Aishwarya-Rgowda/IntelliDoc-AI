from types import SimpleNamespace

from app.services.anomalies import inspect_documents


def test_anomaly_detector_flags_short_text_and_repeated_characters():
    docs = [
        SimpleNamespace(id=1, filename="short.txt", extracted_text="Only a few words here."),
        SimpleNamespace(id=2, filename="broken.txt", extracted_text="x" * 150),
    ]

    findings = inspect_documents(docs)

    assert {item["document_id"] for item in findings} == {1, 2}
    assert any(flag["code"] == "very_short" for item in findings for flag in item["flags"])
    assert any(flag["code"] == "repeated_character_run" for item in findings for flag in item["flags"])


def test_anomaly_detector_returns_empty_for_normal_library():
    docs = [
        SimpleNamespace(id=1, filename="normal.txt", extracted_text=("A reasonably varied document about software engineering. " * 10)),
        SimpleNamespace(id=2, filename="other.txt", extracted_text=("A second varied document describing database design. " * 10)),
    ]
    assert inspect_documents(docs) == []
