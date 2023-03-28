from dataclasses import dataclass


@dataclass
class TranscriptLine():
    """Transcript line model for storing start and end location 
    indices which references to a part of a text in the original
    transcript"""
    transcript_id: int
    line_no: int
    line_text: str
    start_char_loc: int
    end_char_loc: int
