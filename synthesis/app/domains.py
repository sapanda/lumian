from dataclasses import dataclass
from typing import TypedDict


@dataclass
class Transcript:
    """Data model for transcript"""
    id: int
    data: list[dict]

    def __str__(self):
        return '\n'.join([
            f"[{i}] {self.data[i]['text']}" for i in range(len(self.data))
        ])


class SummaryResultOutput(TypedDict):
    """Result model for Summary output"""
    text: str
    references: list[list[int, int]]


class SummaryResult(TypedDict):
    """Result model for Summary"""
    output: list[SummaryResultOutput]
    cost: float


class SynthesisResultOutput(TypedDict):
    """Result model for Synthesis output"""
    text: str
    references: list[int]


class SynthesisResult(TypedDict):
    """Result model for synthesis class"""
    output: list[SynthesisResultOutput]
    cost: float
