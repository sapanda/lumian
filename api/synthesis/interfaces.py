import abc
from typing import List, Dict
from .domains import SynthesisResult, EmbedsResult


class OpenAIClientInterface(abc.ABC):
    """Interface for OpenAI Client"""
    @abc.abstractmethod
    def execute_completion(self, prompt: str,
                           temperature: int,
                           max_tokens: int,
                           ) -> dict:
        """Execute OpenAI API completions request and return the response."""
        pass

    @abc.abstractmethod
    def execute_chat(self, messages: List[Dict[str, str]],
                     temperature: int,
                     max_tokens: int,
                     ) -> dict:
        """Execute OpenAI API chat request and return the response."""
        pass

    @abc.abstractmethod
    def execute_embeds(self, text: str) -> dict:
        """Generate embedding vector for the input text"""
        pass

    @abc.abstractmethod
    def execute_embeds_batch(self, request_list: List[str],
                             object_id: int = None,
                             object_desc: str = None,
                             start_index: int = 0,
                             ) -> dict:
        """Generate embedding vectors for the input strings in request_list"""
        pass


class EmbedsClientInterface(abc.ABC):
    """Interface for Embeddings Client"""
    @abc.abstractmethod
    def upsert(self, vectors: List[dict]):
        """Upsert the vectors into the index"""
        pass

    @abc.abstractmethod
    def search(self, id: int, embedding: List[int], limit: int = 5) -> dict:
        """Retrieve the closest embeds for the input embedding"""
        pass

    @abc.abstractmethod
    def delete(self, id: int):
        """Delete all embeds for the input id"""
        pass


class SynthesisInterface(abc.ABC):

    @abc.abstractmethod
    def summarize_transcript(
            self, indexed_transcript: str, interviewee: str
    ) -> SynthesisResult:
        """Summarize an indexed transcript and return reference indices
        for phrases and sentences in the final summary"""
        pass

    @abc.abstractmethod
    def concise_transcript(
            self, indexed_transcript: str, interviewee: str
    ) -> SynthesisResult:
        """Convert transcript to concise version and return reference indices
        for phrases and sentences in the concise version"""
        pass

    @abc.abstractmethod
    def embed_transcript(
            self,
            transcript_id: int,
            transcript_title: str,
            indexed_transcript: str,
            interviewee: str
    ) -> EmbedsResult:
        """Generate embeds for the transcript"""
        pass

    @abc.abstractmethod
    def query_transcript(
            self,
            transcript_id: int,
            query: str
    ) -> SynthesisResult:
        """Run query against the transcript"""
        pass
