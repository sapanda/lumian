from celery import shared_task
from django.conf import settings
import json
import openai
import pinecone

from transcript.ai.utils import chunk_by_paragraph_groups
from transcript.models import (
    Transcript, SynthesisType, AIChunks, AISynthesis, AIEmbeds, Query
)


# OpenAI Models
OPENAI_MODEL_COMPLETIONS = "text-davinci-003"
OPENAI_MODEL_CHAT = "gpt-3.5-turbo"
OPENAI_MODEL_EMBEDDING = "text-embedding-ada-002"

# OpenAI Pricing (USD per 1k tokens)
OPENAI_PRICING = {
    OPENAI_MODEL_COMPLETIONS: 0.02,
    OPENAI_MODEL_CHAT: 0.002,
    OPENAI_MODEL_EMBEDDING: 0.0004,
}

# OpenAI Parameters
OPENAI_EMBEDDING_DIMENSIONS = 1536

# Pinecone Parameters
PINECONE_REGION = "us-west1-gcp"

# Tweakable Parameters
DEFAULT_TEMPERATURE = 0
DEFAULT_MAX_TOKENS = 600
OPENAI_QUERY_CHARACTER_CUTOFF = 8000
PINECONE_INDEX_NAME = "synthesis-api-dev"


openai.organization = settings.OPENAI_ORG_ID
openai.api_key = settings.OPENAI_API_KEY
pinecone.init(
    api_key=settings.PINECONE_API_KEY,
    environment=PINECONE_REGION
)


def _init_pinecone_index(index_name: str = PINECONE_INDEX_NAME,
                         dimension: int = OPENAI_EMBEDDING_DIMENSIONS
                         ) -> 'pinecone.Index':
    """Initialize the pinecone index."""
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=dimension)
    return pinecone.Index(index_name)


pinecone_index = _init_pinecone_index()


def _calculate_cost(tokens_used: int, model: str) -> float:
    """Calculate the cost of the OpenAI API request."""
    cost = tokens_used / 1000 * OPENAI_PRICING[model]
    return cost


def _execute_openai_completion(prompt: str,
                               model: str,
                               temperature: int = DEFAULT_TEMPERATURE,
                               max_tokens: int = DEFAULT_MAX_TOKENS,
                               ) -> dict:
    """Execute an OpenAI API request and return the response."""

    COMPLETIONS_API_PARAMS = {
        "temperature": temperature,
        "max_tokens": max_tokens,
        "model": model,
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
    }
    return ret_val


def _get_summarized_chunk(text: str,
                          model: str,
                          interviewee: str = None,
                          ) -> dict:
    """Generate a summary for a chunk of the transcript."""

    if interviewee is not None:
        prompter = "detailed summary of only {interviewee}'s comments"
    else:
        prompter = "detailed summary"

    prompt = (f"The following is a section of an interview transcript. "
              f"Please provide a {prompter}. Only answer truthfully and "
              f"don't include anything not in the original transcript: "
              f"\n\n>>>> START OF INTERVIEW \n\n{text}\n\n"
              f">>>> END OF INTERVIEW \n\n"
              f"Detailed Summary: ")

    return _execute_openai_completion(prompt, model)


def _get_summarized_all(text: str,
                        model: str
                        ) -> dict:
    """Generate a summary from a concatenated summary string."""

    prompt = (f"Write a detailed synopsis based on the following notes. "
              f"Only answer truthfully and don't include anything "
              f"not in the original summary: "
              f"\n\n>>>> START OF INTERVIEW NOTES \n\n{text} \n\n>>>>"
              f"END OF INTERVIEW NOTES \n\nSynopsis:")

    return _execute_openai_completion(prompt, model)


def _get_concise_chunk(text: str,
                       model: str,
                       max_examples: int = 1
                       ) -> dict:
    """Generate a concise transcript for a given chunk."""

    prompt = ("The following are sections of an interview transcript. "
              "Please clean it up but still in dialogue form. The speaker "
              "name should always be preserved. Do not add any details "
              "not present in the original transcript. ")

    with open('transcript/examples/eg-concise.json', 'r') as f:
        examples = json.load(f)

    # Add examples to the transcript
    index = 1
    for example in examples:
        input_text = f"Input {index}: ###\n{example['input']}\n###\n"
        output_text = f"Output {index}: ###\n{example['output']}\n###\n"
        prompt = f"{prompt}\n\n{input_text}{output_text}"
        index += 1

        if index > max_examples:
            break

    prompt = (f"{prompt}\n\nInput {index}: ###\n{text}\n###\n"
              f"Output {index}:###\n\n###")

    return _execute_openai_completion(prompt, model)


def _generate_chunks(tct: Transcript) -> 'list[str]':
    interviewee = tct.interviewee_names[0]  # Support one interviewee for now
    paragraph_groups = chunk_by_paragraph_groups(
        tct.transcript,
        interviewee,
    )
    return paragraph_groups


def _process_chunks_for_summaries(tct: Transcript,
                                  chunks: 'list[str]') -> AIChunks:
    """Chunk up the transcript and generate summaries for each chunk."""
    model = OPENAI_MODEL_CHAT
    interviewee = tct.interviewee_names[0]  # Support one interviewee for now

    summaries = []
    tokens_used = []
    for chunk in chunks:
        response = _get_summarized_chunk(chunk, model, interviewee)
        summaries.append(response['output'])
        tokens_used.append(response['tokens_used'])

    summary_chunks = AIChunks.objects.create(
        transcript=tct,
        chunk_type=SynthesisType.SUMMARY,
        chunks=chunks,
        chunks_processed=summaries,
        tokens_used=tokens_used,
        cost=_calculate_cost(sum(tokens_used), model),
        model_name=model,
    )

    summary_chunks.save()
    return summary_chunks


def _process_chunks_for_concise(tct: Transcript,
                                chunks: 'list[str]') -> AIChunks:
    """
    Chunk up the transcript and generate concise transcripts for each chunk.
    """
    model = OPENAI_MODEL_CHAT

    concise_chunks = []
    tokens_used = []
    for chunk in chunks:
        response = _get_concise_chunk(chunk, model)
        concise_chunks.append(response['output'])
        tokens_used.append(response['tokens_used'])

    concise_chunks = AIChunks.objects.create(
        transcript=tct,
        chunk_type=SynthesisType.CONCISE,
        chunks=chunks,
        chunks_processed=concise_chunks,
        tokens_used=tokens_used,
        cost=_calculate_cost(sum(tokens_used), model),
        model_name=model,
    )

    concise_chunks.save()
    return concise_chunks


def _generate_summary(tct: Transcript, chunks: AIChunks) -> AISynthesis:
    """Generate the AISynthesis summary for the transcript."""
    concat_summary = " ".join(chunks.chunks_processed)
    model = OPENAI_MODEL_COMPLETIONS

    response = _get_summarized_all(concat_summary, model)

    summary_cost = _calculate_cost(response['tokens_used'], model)
    total_cost = chunks.cost + summary_cost

    summary_obj = AISynthesis.objects.create(
        transcript=tct,
        output_type=SynthesisType.SUMMARY,
        output=response['output'],
        tokens_used=response['tokens_used'],
        total_cost=total_cost,
        model_name=model,
    )
    summary_obj.save()
    return summary_obj


def _generate_concise(tct: Transcript, chunks: AIChunks) -> AISynthesis:
    """Generate the AISynthesis concise transcript."""
    concise_transcript = "\n\n".join(chunks.chunks_processed)

    concise_obj = AISynthesis.objects.create(
        transcript=tct,
        output_type=SynthesisType.CONCISE,
        output=concise_transcript,
        tokens_used=0,
        total_cost=chunks.cost,
        model_name=None,
    )
    concise_obj.save()
    return concise_obj


def _create_batches_for_embeds(content_list: 'list[str]',
                               max_length: int) -> 'list[list[str]]':
    """
    Split the content_list into batches of the appropriate
    size for sending to the OpenAI Embeddings API.
    """
    batches = []
    request_list = []
    request_length = 0
    for content in content_list:

        # TODO: This assumes no 'content' string is longer than
        # max_length. Chunking algorithm needs to factor this limit in
        if len(content) + request_length > max_length:
            batches.append(request_list)
            request_list = []
            request_length = 0

        request_list.append(content)
        request_length += len(content)

    if request_list:
        batches.append(request_list)

    return batches


def _execute_openai_embeds(tct: Transcript,
                           request_list: 'list[str]',
                           start_index: int) -> dict:
    """Generate embeds for the input strings using Open AI."""
    ret_val = None

    if request_list:
        result = openai.Embedding.create(
            model=OPENAI_MODEL_EMBEDDING,
            input=request_list
        )
        token_count = result["usage"]["total_tokens"]
        embeds = [record['embedding'] for record in result['data']]

        meta = [{
            'text': line,
            'transcript_id': tct.id,
            'transcript_title': tct.title,
            } for line in request_list]

        end_index = start_index + len(request_list)
        request_ids = [f'{str(tct.id)}-{str(n)}'
                       for n in range(start_index, end_index)]
        to_upsert = zip(request_ids, embeds, meta)

        ret_val = {
            'upsert_list': list(to_upsert),
            'token_count': token_count,
            'request_ids': request_ids,
        }

    return ret_val


def _execute_openai_embeds_and_upsert(tct: Transcript,
                                      index: 'pinecone.Index',
                                      content_list: 'list[str]') -> int:
    """Generate embeds for the input strings using Open AI."""

    # TODO: OpenAI only allows max 8192 tokens per API call
    # For now we'll limit to 20000 characters per API call
    # But in the future use tiktoken to get exact token count
    MAX_CHAR_LENGTH = 20000

    batches = _create_batches_for_embeds(content_list, MAX_CHAR_LENGTH)
    start_index = 0
    token_count = 0
    request_ids = []
    for batch in batches:
        result = _execute_openai_embeds(tct, batch, start_index)
        upsert_list = result['upsert_list']
        token_count += result['token_count']
        request_ids += result['request_ids']
        start_index += len(batch)

        index.upsert(vectors=upsert_list,
                     namespace=settings.PINECONE_NAMESPACE)

    ret_val = {
        'token_count': token_count,
        'request_ids': request_ids,
    }

    return ret_val


def _generate_embeds(tct: Transcript, chunks: 'list[str]') -> None:
    """Generate the embeds for the transcript."""
    result = _execute_openai_embeds_and_upsert(tct, pinecone_index, chunks)
    cost = _calculate_cost(result['token_count'], OPENAI_MODEL_EMBEDDING)

    embeds_obj = AIEmbeds.objects.create(
        transcript=tct,
        chunks=chunks,
        pinecone_ids=result['request_ids'],
        index_cost=cost,
    )
    embeds_obj.save()
    return embeds_obj


@shared_task
def generate_synthesis(transcript_id):
    """Generate an AI-synthesized summary for a transcript."""
    print(f'\n\n\nTranscript ID: {transcript_id}\n\n\n')
    tct = Transcript.objects.get(id=transcript_id)
    chunks = _generate_chunks(tct)

    summary_chunks = _process_chunks_for_summaries(tct, chunks)
    summary_obj = _generate_summary(tct, summary_chunks)

    concise_chunks = _process_chunks_for_concise(tct, chunks)
    concise_obj = _generate_concise(tct, concise_chunks)

    embeds_obj = _generate_embeds(tct, chunks)

    tct.cost = summary_obj.total_cost + \
        concise_obj.total_cost + embeds_obj.index_cost
    tct.save()


def _execute_pinecone_search(tct: Transcript, query: str) -> dict:
    """Retrieve the relevant embeds from Pinecone for the given query."""
    embed_result = openai.Embedding.create(input=query,
                                           model=OPENAI_MODEL_EMBEDDING)
    embedding = embed_result['data'][0]['embedding']
    query_result = pinecone_index.query(
        [embedding],
        filter={
            "transcript_id": {"$eq": tct.id}
        },
        top_k=5,
        include_metadata=True,
        namespace=settings.PINECONE_NAMESPACE,
    )

    return query_result


def _context_from_search_results(search_results: dict,
                                 max_context_length: int
                                 = OPENAI_QUERY_CHARACTER_CUTOFF
                                 ) -> 'list[str]':
    """
    Parse the search_results and return a context string
    list with total length under max_context_length
    """
    chosen_sections = []
    total_length = 0
    for match in search_results['matches']:
        item = match['metadata']['text']
        # TODO: Verify chunks are not larger than cutoff
        if total_length + len(item) > max_context_length:
            break

        chosen_sections.append(item)
        total_length += len(item)

    return chosen_sections


def _execute_openai_query(query: str,
                          model: str,
                          chosen_sections: 'list[str]'
                          ) -> dict:
    """Generate a summary from a concatenated summary string."""

    prompt = (f'Answer the question as truthfully as possible using '
              f'the provided context, which consists of excerpts from '
              f'interviews. If the answer is not contained within the '
              f'text below, say "I don\'t know."\n\nContext:\n'
              f'{"".join(chosen_sections)}Q: {query}\nA:')

    return _execute_openai_completion(prompt, model)


# TODO: Should this and other OpenAI logic be in tasks.py?
def run_openai_query(tct: Transcript, query: str) -> Query:
    """Generate the OpenAI query for the given transcript."""
    search_results = _execute_pinecone_search(tct, query)
    chosen_sections = _context_from_search_results(search_results)
    model = OPENAI_MODEL_CHAT
    response = _execute_openai_query(
        query, model=model, chosen_sections=chosen_sections
    )
    query_cost = _calculate_cost(response['tokens_used'], model)

    matches = search_results['matches']
    search_values = [match['metadata']['text'] for match in matches]
    search_scores = [match['score'] for match in matches]

    query_obj = Query.objects.create(
        transcript=tct,
        query=query,
        result=response['output'],
        search_values=search_values,
        search_scores=search_scores,
        query_cost=query_cost,
    )
    query_obj.save()

    tct.cost = float(tct.cost) + query_obj.query_cost
    tct.save()

    return query_obj
