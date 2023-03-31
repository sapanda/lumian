from app.utils import (
    split_text_into_multiple_lines_for_speaker,
    split_indexed_transcript_lines_into_chunks,
    split_and_extract_indices,
    split_indexed_lines_into_chunks
)

text = """Jason: "Some Text Some text"

Shawn: "Some Text. Some Text. Some Text and Some Text."

"""

multiple_line_split_text_for_speaker_results = [
    {'text': 'Jason: Some Text Some text', 'start': 8, 'end': 27},
    {'text': 'Shawn: Some Text.', 'start': 38, 'end': 48},
    {'text': 'Shawn: Some Text.', 'start': 48, 'end': 59},
    {'text': 'Shawn: Some Text and Some Text.', 'start': 59, 'end': 84}]

indexed_notes = """[0] Some text Some text Some text Some text Some text.
[1] Some text Some text Some text
[2] Some text Some text Some text Some text Some text Some text Some text,
[3] Some text Some text Some text Some text.
[4] Some text Some text Some text Some text Some text Some text."""

indexed_lines_into_chunks_indexed_chunks_results = [
    [
        '[0] Some text Some text Some text Some text Some text.',
        '[1] Some text Some text Some text',
        '[2] Some text Some text Some text Some text Some text Some text Some\
 text,'],
    [
        '[3] Some text Some text Some text Some text.',
        '[4] Some text Some text Some text Some text Some text Some text.'
    ]
]

indexed_transcript = """[0] Shawn: Some text Some text Some text Some\
 text Some text.
[1] Jason: Some text Some text Some text
[2] Shawn: Some text Some text Some text Some text Some text Some text Some\
 text,
[3] Jason: Some text Some text Some text Some text.
[4] Shawn: Some text Some text Some text Some text Some text Some text."""

indexed_transcript_into_chunks_indexed_chunks_results = [
    [
        '[0] Shawn: Some text Some text Some text Some text Some text.',
        '[1] Jason: Some text Some text Some text'
    ],
    [
        '[2] Shawn: Some text Some text Some text Some text Some text Some\
 text Some text,',
        '[3] Jason: Some text Some text Some text Some text.'
    ],
    [
        '[4] Shawn: Some text Some text Some text Some text Some text Some\
 text.'
    ]
]

notes_with_references = "Some text Some text Some text (2,3).\
 Some text Some text Some text (8-10), Some text Some text Some text Some text\
(1, 21-25, 28)."

notes_indices_references = [
    {'text': 'Some text Some text Some text', 'references': [2, 3]},
    {'text': '. Some text Some text Some text', 'references': [8, 9, 10]},
    {'text': ', Some text Some text Some text Some text',
     'references': [1, 21, 22, 23, 24, 25, 28]}]


def test_split_text_into_multiple_lines_for_speaker():
    result = split_text_into_multiple_lines_for_speaker(
        text, line_min_size=2)
    assert result == multiple_line_split_text_for_speaker_results


def test_split_indexed_lines_into_chunks():
    result = split_indexed_lines_into_chunks(
        indexed_notes, chunk_min_words=20)
    assert result == indexed_lines_into_chunks_indexed_chunks_results


def test_split_indexed_transcript_lines_into_chunks():
    result = split_indexed_transcript_lines_into_chunks(
        indexed_transcript, interviewee="Jason", chunk_min_words=10)
    assert indexed_transcript_into_chunks_indexed_chunks_results == result


def test_split_and_extract_indices():
    result = split_and_extract_indices(notes_with_references)
    assert result == notes_indices_references
