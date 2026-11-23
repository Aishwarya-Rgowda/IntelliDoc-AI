from app.services.summarizer import summarize_text


def test_summary_selects_relevant_sentences_in_original_order():
    text = (
        "Python is a programming language used for automation and data analysis. "
        "The weather is sunny today in the city. "
        "Python supports functions, loops, and reusable modules for software development."
    )

    summary, original_count, summary_count = summarize_text(text, max_sentences=2)

    assert "Python is a programming language" in summary
    assert "Python supports functions" in summary
    assert summary.index("programming language") < summary.index("supports functions")
    assert summary_count < original_count


def test_summary_handles_empty_text():
    summary, original_count, summary_count = summarize_text("")

    assert summary == ""
    assert original_count == 0
    assert summary_count == 0
