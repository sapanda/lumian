from dataclasses import dataclass
from typing import (
    TypedDict,
    List,
    Optional
)


@dataclass
class Transcript:
    """Data model for transcript"""
    id: int
    data: List[dict]

    def __str__(self):
        return '\n'.join([
            f"[{i}] {self.data[i]['text']}" for i in range(len(self.data))
        ])


class CitationResultOutput(TypedDict):
    """Result model for standard request output"""
    text: str
    references: List[List[int]]


class CitationResult(TypedDict):
    """Result model for standard request"""
    output: List[CitationResultOutput]
    prompt: str
    cost: float


class SynthesisResultOutput(TypedDict):
    """Result model for Synthesis output"""
    text: str
    references: List[int]


class MetadataResult(TypedDict):
    """Result model for Metadata"""
    title: str
    interviewees: List[str]
    interviewers: List[str]
    cost: float
    message: str


class SynthesisResult(TypedDict):
    """Result model for synthesis class"""
    output: List[SynthesisResultOutput]
    prompt: str
    cost: float
    metadata: Optional[MetadataResult]


class SynthesisResponse(TypedDict):
    """Result model for standard request"""
    output: List[CitationResultOutput]
    prompt: str
    cost: float
    metadata: Optional[MetadataResult]


class EmbedsResult(TypedDict):
    """Result model for Embeds"""
    cost: float
