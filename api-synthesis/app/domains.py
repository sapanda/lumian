from dataclasses import dataclass
from typing import TypedDict


@dataclass
class Transcript:
    """Data model for transcript"""
    id: int
    data: 'list[dict]'

    def __str__(self):
        return '\n'.join([
            f"[{i}] {self.data[i]['text']}" for i in range(len(self.data))
        ])


class CitationResultOutput(TypedDict):
    """Result model for standard request output"""
    text: str
    references: 'list[list[int, int]]'


class CitationResult(TypedDict):
    """Result model for standard request"""
    output: 'list[CitationResultOutput]'
    prompt: str
    cost: float


class SynthesisResultOutput(TypedDict):
    """Result model for Synthesis output"""
    text: str
    references: 'list[int]'


class SynthesisResult(TypedDict):
    """Result model for synthesis class"""
    output: 'list[SynthesisResultOutput]'
    prompt: str
    cost: float
    metadata: 'MetadataResult'


class SynthesisResponse(TypedDict):
    """Result model for standard request"""
    output: 'list[CitationResultOutput]'
    prompt: str
    cost: float
    metadata: 'MetadataResult'


class EmbedsResult(TypedDict):
    """Result model for Embeds"""
    cost: float


class MetadataResult(TypedDict):
    """Result model for Metadata"""
    title: str
    interviewees: 'list[str]'
    interviewers: 'list[str]'
    cost: float
    message: str
