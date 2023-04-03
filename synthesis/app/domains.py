from dataclasses import dataclass


@dataclass
class Transcript:
    """Data model for transcript"""
    id: int
    data: list[dict]

    def __str__(self):
        return '\n'.join([
            f"[{i}] {self.data[i]['text']}" for i in range(len(self.data))
        ])
