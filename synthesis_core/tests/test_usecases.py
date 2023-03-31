from app.usecases import (
    save_transcript,
    get_transcript_summary
)
from app.repositories import TranscriptRepository
from app.domains import TranscriptLine

text = """Jason: "Some Text Some text"

Shawn: "Some Text. Some Text. Some Text and Some Text."

"""

repo = TranscriptRepository(conn=None)
lines = [("some text", 0, 23), ("some text", 23, 50)]
lines = [
    TranscriptLine(
        transcript_id=0,
        line_text=lines[i][0],
        start_char_loc=lines[i][1],
        end_char_loc=lines[i][2],
        line_no=i
    ) for i in range(len(lines))]


def test_save_transcript(monkeypatch):
    monkeypatch.setattr(
        repo, 'save_transcript', lambda lines: None)
    save_transcript(transcript_id=0, transcript=text, repo=repo)


def test_get_transcript_summary(monkeypatch):
    monkeypatch.setattr(
        'app.usecases.summarize_transcript',
        lambda new_text, interviewee: ([("Some text", [0, 1])], 0.003))

    monkeypatch.setattr(
        repo,
        'get_transcript',
        lambda transcript_id: lines)
    result = get_transcript_summary(0, "Jason", repo)
    test_result = {
        'output': [
            {
                'text': 'Some text',
                'references': [[0, 23], [23, 50]]
            }
        ],
        'cost': 0.003
    }
    assert result == test_result
