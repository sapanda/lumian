import abc
from .domains import Transcript


class OpenAIClientInterface(abc.ABC):

    @abc.abstractmethod
    def execute_completion(self, prompt: str,
                           model: str,
                           temperature: int,
                           max_tokens: int,
                           ) -> dict:
        pass


class TranscriptRepositoryInterface(abc.ABC):

    @abc.abstractmethod
    def get(self, id: int) -> Transcript:
        pass

    @abc.abstractmethod
    def save(self, transcript: Transcript):
        pass

    @abc.abstractmethod
    def delete(self, id: int):
        pass

    @abc.abstractmethod
    def replace(self, transcript: Transcript):
        pass


class SynthesisInterface(abc.ABC):

    @abc.abstractmethod
    def summarize_transcript(
            self, indexed_transcript: str, interviewee: str
    ) -> dict:
        pass
