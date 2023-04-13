import openai
from openai.error import Timeout
from retry import retry

from .errors import OpenAITimeoutException
from .interfaces import OpenAIClientInterface


# Models
OPENAI_MODEL_COMPLETIONS = "text-davinci-003"
OPENAI_MODEL_CHAT = "gpt-3.5-turbo"
OPENAI_MODEL_EMBEDDING = "text-embedding-ada-002"

# Pricing
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

    def _calculate_cost(self, tokens_used: int, model: str) -> float:
        """Calculate the cost of the OpenAI API request."""
        cost = tokens_used / 1000 * OPENAI_PRICING[model]
        return cost

    # TODO: Need to save all prompts to a log
    @retry(OpenAITimeoutException, tries=3, delay=5, backoff=2)
    def execute_completion(self,
                           prompt: str,
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
            if model == OPENAI_MODEL_CHAT:
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

            tokens_used = response["usage"]["total_tokens"]
            cost = self._calculate_cost(tokens_used, model)

            ret_val = {
                "prompt": prompt,
                "output": summary,
                "tokens_used": tokens_used,
                "cost": cost
            }
        except Timeout:
            raise OpenAITimeoutException(
                detail="OpenAI could not complete the completions"
                "request in time")

        return ret_val

    @retry(OpenAITimeoutException, tries=3, delay=5, backoff=2)
    def execute_embeds(self, text: str) -> dict:
        """Generate embedding vector for the input text"""
        try:
            model = OPENAI_MODEL_EMBEDDING
            result = openai.Embedding.create(
                model=model,
                input=text
            )

            tokens_used = result["usage"]["total_tokens"]
            cost = self._calculate_cost(tokens_used, model)

            ret_val = {
                "embedding": result['data'][0]['embedding'],
                "tokens_used": tokens_used,
                "cost": cost
            }
        except Timeout:
            raise OpenAITimeoutException(
                detail="OpenAI could not complete the embedding"
                "request in time")

        return ret_val

    @retry(OpenAITimeoutException, tries=3, delay=5, backoff=2)
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
                model = OPENAI_MODEL_EMBEDDING
                result = openai.Embedding.create(
                    model=model,
                    input=request_list
                )
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
                cost = self._calculate_cost(tokens_used, model)

                ret_val = {
                    "upsert_list": list(to_upsert),
                    "request_ids": request_ids,
                    "tokens_used": tokens_used,
                    "cost": cost
                }
        except Timeout:
            raise OpenAITimeoutException(
                detail="OpenAI could not complete the completions"
                "request in time")

        return ret_val
