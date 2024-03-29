class SynthesisAPIException(Exception):
    """Base class for Synthesis API Exception"""

    def __init__(self, detail: str):
        self.detail = detail


class OpenAITimeoutException(SynthesisAPIException):
    """Timeout exception for openai timeout error"""
    pass


class OpenAIRateLimitException(SynthesisAPIException):
    """Rate Limit exception for openai rate limit error"""
    pass


class PineconeException(SynthesisAPIException):
    """Generic exception when using Pinecone APIs"""
    pass


class ObjectNotFoundException(SynthesisAPIException):
    """Exception for object not found in storage"""
    pass


class ObjectAlreadyPresentException(SynthesisAPIException):
    """Exception for creating an object which is already present"""
    pass
