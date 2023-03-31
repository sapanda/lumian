from app.core import (
    summarize_transcript,
    summarize_text
)
transcript = """[0] Jason: Some text Some text Some text
[1] Jason: Some text Some text Some text
[2] Shawn: Some text Some text Some text
[3] Jason: Some text Some text Some text
[4] Jason: Some text Some text Some text Some text Some text Some text
[5] Shawn: Some text Some text Some text Some text
"""

text = """[0] Some text Some text Some text
[1] Some text Some text Some text
[2] Some text Some text Some text
[3] Some text Some text Some text
[4] Some text Some text Some text Some text Some text Some text
[5] Some text Some text Some text Some text
"""


def test_summarize_transcript(monkeypatch):
    def ret_val1(text, interviewee): return {
        "output": "Some text (0)",
        "tokens_used": 200,
        "cost": 0.005
    }

    def ret_val2(text): return {
        "output": "Some text (0)",
        "tokens_used": 200,
        "cost": 0.005
    }
    monkeypatch.setattr(
        "app.core.openai_summarize_chunk", ret_val1)
    monkeypatch.setattr(
        "app.core.openai_summarize_full", ret_val2)
    result = summarize_transcript(transcript, "Jason")
    assert result == ([('Some text', [0])], 0.01)


def test_summarize_text(monkeypatch):
    def ret_val2(text): return {
        "output": "Some text (0)",
        "tokens_used": 200,
        "cost": 0.005
    }
    monkeypatch.setattr(
        "app.core.openai_summarize_full", ret_val2)
    result = summarize_text(text)
    assert result == ([('Some text', [0])], 0.005)
