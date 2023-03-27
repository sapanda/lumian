from dataclasses import dataclass

@dataclass
class TranscriptLine():
    transcript_id: int
    line_no: int
    line_text: str
    start_char_loc: int
    end_char_loc: int
