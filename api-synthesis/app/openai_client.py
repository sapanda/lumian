from enum import Enum
import logging
import openai
from openai.error import Timeout, RateLimitError
from retry import retry

from .errors import OpenAITimeoutException, OpenAIRateLimitException
from .interfaces import OpenAIClientInterface


# Pricing
class OpenAIPricing(Enum):
    COMPLETIONS = 0.02
    CHAT = 0.002
    EMBEDDINGS = 0.0004


# Models
OPENAI_MODEL_COMPLETIONS = "text-davinci-003"
OPENAI_MODEL_CHAT = "gpt-3.5-turbo"
OPENAI_MODEL_EMBEDDING = "text-embedding-ada-002"

# Model Params / TODO: Move to env vars
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 600

# Retry Params
RETRY_TRIES = 3
RETRY_DELAY_TIMEOUT = 5
RETRY_DELAY_RATELIMIT = 5
RETRY_BACKOFF = 2

# API Types
OPENAI_API_TYPE = "open_ai"
AZURE_API_TYPE = "azure"

logger = logging.getLogger()


class OpenAIClient(OpenAIClientInterface):
    def __init__(self, **kwargs) -> None:
        self.completions_api_type = kwargs.get('completions_api_type')
        self.completions_api_key = kwargs.get('completions_api_key')
        self.completions_api_base = kwargs.get('completions_api_base')
        self.completions_api_version = kwargs.get('completions_api_version')
        self.completions_model = kwargs.get('completions_model')
        self.embeddings_api_type = kwargs.get('embeddings_api_type')
        self.embeddings_api_key = kwargs.get('embeddings_api_key')
        self.embeddings_api_base = kwargs.get('embeddings_api_base')
        self.embeddings_api_version = kwargs.get('embeddings_api_version')
        self.embeddings_model = kwargs.get('embeddings_model')

        if self.completions_model is None:
            self.completions_model = OPENAI_MODEL_CHAT
        if self.embeddings_model is None:
            self.embeddings_model = OPENAI_MODEL_EMBEDDING

    def _calculate_cost(self, tokens_used: int,
                        pricing: OpenAIPricing) -> float:
        """Calculate the cost of the OpenAI API request."""
        cost = tokens_used / 1000 * pricing.value
        return cost

    def _build_completions_params(self,
                                  temperature: int = DEFAULT_TEMPERATURE,
                                  max_tokens: int = DEFAULT_MAX_TOKENS
                                  ) -> dict:
        """Creates the parameters for the OpenAI API Completions request."""
        params = {
            "api_key": self.completions_api_key,
            "api_type": self.completions_api_type,
            "api_base": self.completions_api_base,
            "api_version": self.completions_api_version,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if self.completions_api_type == AZURE_API_TYPE:
            params["engine"] = self.completions_model
        else:
            params["model"] = self.completions_model
        return params

    @retry(OpenAIRateLimitException, tries=RETRY_TRIES,
           delay=RETRY_DELAY_RATELIMIT, backoff=RETRY_BACKOFF)
    @retry(OpenAITimeoutException, tries=RETRY_TRIES,
           delay=RETRY_DELAY_TIMEOUT, backoff=RETRY_BACKOFF)
    def execute_completion(self,
                           prompt: str,
                           temperature: int = DEFAULT_TEMPERATURE,
                           max_tokens: int = DEFAULT_MAX_TOKENS,
                           ) -> dict:
        """Execute an OpenAI API request and return the response."""
        try:
            params = self._build_completions_params(
                temperature=temperature, max_tokens=max_tokens)

            if self.completions_model == OPENAI_MODEL_COMPLETIONS:
                response = openai.Completion.create(
                    prompt=prompt, **params)
                result = response["choices"][0]["text"].strip(" \n")
                tokens_used = response["usage"]["total_tokens"]
                cost = self._calculate_cost(tokens_used,
                                            OpenAIPricing.COMPLETIONS)
            else:
                messages = [{"role": "user", "content": prompt}]
                response = openai.ChatCompletion.create(
                    messages=messages, **params)
                result = response["choices"][0]["message"]["content"].strip(
                    " \n")
                tokens_used = response["usage"]["total_tokens"]
                cost = self._calculate_cost(tokens_used,
                                            OpenAIPricing.CHAT)

            ret_val = {
                "prompt": prompt,
                "output": result,
                "tokens_used": tokens_used,
                "cost": cost
            }
        except Timeout as e:
            logger.exception("OpenAI Completion Timeout", exc_info=e)
            raise OpenAITimeoutException(
                detail="OpenAI could not complete the requests in time")
        except RateLimitError as e:
            logger.exception("OpenAI Completion hit Rate Limit", exc_info=e)
            raise OpenAIRateLimitException(
                detail="OpenAI rate limit exceeded, please try again later")

        return ret_val

    def _build_embeddings_params(self) -> dict:
        """Creates the parameters for the OpenAI API Embeddings request."""
        params = {
            "api_key": self.embeddings_api_key,
            "api_type": self.embeddings_api_type,
            "api_base": self.embeddings_api_base,
            "api_version": self.embeddings_api_version,
        }
        if self.completions_api_type == AZURE_API_TYPE:
            params["engine"] = self.embeddings_model
        else:
            params["model"] = self.embeddings_model
        return params

    @retry(OpenAIRateLimitException, tries=RETRY_TRIES,
           delay=RETRY_DELAY_RATELIMIT, backoff=RETRY_BACKOFF)
    @retry(OpenAITimeoutException, tries=RETRY_TRIES,
           delay=RETRY_DELAY_TIMEOUT, backoff=RETRY_BACKOFF)
    def execute_embeds(self, text: str) -> dict:
        """Generate embedding vector for the input text"""
        try:
            params = self._build_embeddings_params()
            result = openai.Embedding.create(input=text, **params)

            tokens_used = result["usage"]["total_tokens"]
            cost = self._calculate_cost(tokens_used, OpenAIPricing.EMBEDDINGS)

            ret_val = {
                "embedding": result['data'][0]['embedding'],
                "tokens_used": tokens_used,
                "cost": cost
            }
        except Timeout as e:
            logger.exception("OpenAI Embedding Timeout", exc_info=e)
            raise OpenAITimeoutException(
                detail="OpenAI could not complete the requests in time")
        except RateLimitError as e:
            logger.exception("OpenAI Embedding hit Rate Limit", exc_info=e)
            raise OpenAIRateLimitException(
                detail="OpenAI rate limit exceeded, please try again later")

        return ret_val

    @retry(OpenAIRateLimitException, tries=RETRY_TRIES,
           delay=RETRY_DELAY_RATELIMIT, backoff=RETRY_BACKOFF)
    @retry(OpenAITimeoutException, tries=RETRY_TRIES,
           delay=RETRY_DELAY_TIMEOUT, backoff=RETRY_BACKOFF)
    def execute_embeds_batch(self,
                             request_list: 'list[str]',
                             object_id: int = None,
                             object_desc: str = None,
                             start_index: int = 0,
                             ) -> dict:
        """
        Generate embedding vectors for the input strings in request_list
        """
        try:
            if request_list:
                params = self._build_embeddings_params()
                result = openai.Embedding.create(input=request_list, **params)
                embeds = [record['embedding'] for record in result['data']]

                meta = []
                for line in request_list:
                    data = {'text': line}
                    if object_id is not None:
                        data['object_id'] = object_id
                    if object_desc is not None:
                        data['object_desc'] = object_desc
                    meta.append(data)

                end_index = start_index + len(request_list)
                request_ids = [f'{str(object_id)}-{str(n)}'
                               for n in range(start_index, end_index)]
                to_upsert = zip(request_ids, embeds, meta)

                tokens_used = result["usage"]["total_tokens"]
                cost = self._calculate_cost(tokens_used,
                                            OpenAIPricing.EMBEDDINGS)

                ret_val = {
                    "upsert_list": list(to_upsert),
                    "request_ids": request_ids,
                    "tokens_used": tokens_used,
                    "cost": cost
                }
        except Timeout as e:
            logger.exception("OpenAI Embedding Batch Timeout", exc_info=e)
            raise OpenAITimeoutException(
                detail="OpenAI could not complete the requests in time")
        except RateLimitError as e:
            logger.exception("OpenAI Embedding Batch Rate Limit", exc_info=e)
            raise OpenAIRateLimitException(
                detail="OpenAI rate limit exceeded, please try again later")

        return ret_val
