import openai, os, time

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

# Open AI Setup
openai.organization = os.environ.get('OPENAI_ORG_ID')
openai.api_key = os.environ.get('OPENAI_API_KEY')

def retry(max_count: int, backoff: int, exponential: bool):
    def inner1(func):
        def inner2(*params):
            i = 0 
            while i < max_count:
                print(f"Retrying : {func}")
                try: 
                    result = func(*params)
                    return result
                except Exception as e:
                    print(e)
                    i += 1
                    time.sleep(backoff)
                    if exponential:
                        backoff *= 2
                    
        return inner2
    return inner1

# @retry(max_count=1, backoff=0, exponential=False)
def execute_openai_completion(prompt: str,
                               model: str = OPENAI_MODEL_CHAT,
                               temperature: int = DEFAULT_TEMPERATURE,
                               max_tokens: int = DEFAULT_MAX_TOKENS,
                               ) -> dict:
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
        summary = response["choices"][0]["message"]["content"].strip(" \n")
    else:
        response = openai.Completion.create(
            prompt=prompt,
            **COMPLETIONS_API_PARAMS
        )
        summary = response["choices"][0]["text"].strip(" \n")

    ret_val = {
        "output": summary,
        "tokens_used": response["usage"]["total_tokens"],
        "cost": response["usage"]["total_tokens"]*OPENAI_PRICING[model]/1000
    }
    return ret_val
