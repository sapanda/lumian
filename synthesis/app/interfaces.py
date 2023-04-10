import abc
from .domains import Transcript, SynthesisResult


class OpenAIClientInterface(abc.ABC):
    """Interface for  OpenAI Client"""
    @abc.abstractmethod
    def execute_completion(self, prompt: str,
                           model: str,
                           temperature: int,
                           max_tokens: int,
                           ) -> dict:
        """Method for making openai completions request
        and returning a response"""
        pass


class TranscriptRepositoryInterface(abc.ABC):
    """Interface OpenAI Client"""
    @abc.abstractmethod
    def get(self, id: int) -> Transcript:
        """Get a transcript from storage"""
        pass

    @abc.abstractmethod
    def save(self, transcript: Transcript):
        """Save transcript to storage"""
        pass

    @abc.abstractmethod
    def delete(self, id: int):
        """Replace transcript in storage"""
        pass

    @abc.abstractmethod
    def replace(self, transcript: Transcript):
        """Delete transcript of transcript"""
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
