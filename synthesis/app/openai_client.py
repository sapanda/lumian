from .interfaces import OpenAIClientInterface
import openai
from openai.error import Timeout
from .errors import OpenAITimeoutException
from retry import retry
# Models
OPENAI_MODEL_COMPLETIONS = "text-davinci-003"
OPENAI_MODEL_CHAT = "gpt-3.5-turbo"
OPENAI_MODEL_EMBEDDING = "text-embedding-ada-002"

#
OPENAI_PRICING = {
    OPENAI_MODEL_COMPLETIONS: 0.02,
    OPENAI_MODEL_CHAT: 0.002,
    OPENAI_MODEL_EMBEDDING: 0.0004,
}

# Model Params
DEFAULT_TEMPERATURE = 0
DEFAULT_MAX_TOKENS = 600


class OpenAIClient(OpenAIClientInterface):
    def __init__(self, org_id: str, api_key: str) -> None:
        openai.organization = org_id
        openai.api_key = api_key

    @retry(OpenAITimeoutException, tries=3, delay=5, backoff=2)
    def execute_completion(self, prompt: str,
                           model: str = OPENAI_MODEL_CHAT,
                           temperature: int = DEFAULT_TEMPERATURE,
                           max_tokens: int = DEFAULT_MAX_TOKENS,
                           ) -> dict:
        """Execute an OpenAI API request and return the response."""
        try:
            COMPLETIONS_API_PARAMS = {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "model": model
            }
            if model is OPENAI_MODEL_CHAT:
                messages = [{"role": "user", "content": prompt}]
                response = openai.ChatCompletion.create(
                    messages=messages,
                    **COMPLETIONS_API_PARAMS
                )
                summary = response["choices"][0]["message"]["content"].strip(
                    " \n")
            else:
                response = openai.Completion.create(
                    prompt=prompt,
                    **COMPLETIONS_API_PARAMS
                )
                summary = response["choices"][0]["text"].strip(" \n")
            cost = response["usage"]["total_tokens"] * \
                OPENAI_PRICING[model]/1000
            ret_val = {
                "output": summary,
                "tokens_used": response["usage"]["total_tokens"],
                "cost": cost
            }
        except Timeout:
            raise OpenAITimeoutException(
                detail="OpenAI could not complete the completions"
                "request in time")

        return ret_val
