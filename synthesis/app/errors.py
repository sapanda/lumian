class SynthesisAPIException(Exception):
    """Base class for Synthesis API Exception"""

    def __init__(self, detail: str):
        self.detail = detail


class OpenAITimeoutException(SynthesisAPIException):
    """Timeout exception for openai timeout error"""
    pass


class ObjectNotFoundException(SynthesisAPIException):
    """Exception for object not found in storage"""
    pass
