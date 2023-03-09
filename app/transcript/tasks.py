from celery import shared_task
from django.conf import settings
import json
import openai

from transcript.ai.utils import chunk_by_paragraph_groups
from transcript.models import (
    Transcript, AIChunks, AISynthesis, SynthesisType
)


# OpenAI Models
OPENAI_MODEL_COMPLETIONS = "text-davinci-003"
OPENAI_MODEL_CHAT = "gpt-3.5-turbo"
OPENAI_MODEL_EMBEDDING = "text-embedding-ada-002"

# OpenAI Pricing (USD per 1k tokens)
OPEN_AI_PRICING = {
    OPENAI_MODEL_COMPLETIONS: 0.02,
    OPENAI_MODEL_CHAT: 0.002,
    OPENAI_MODEL_EMBEDDING: 0.0004,
}

# Model Defaults
DEFAULT_TEMPERATURE = 0
DEFAULT_MAX_TOKENS = 600

openai.organization = settings.OPENAI_ORG_ID
openai.api_key = settings.OPENAI_API_KEY


def _calculate_cost(tokens_used: int, model: str) -> float:
    """Calculate the cost of the OpenAI API request."""
    cost = tokens_used / 1000 * OPEN_AI_PRICING[model]
    return cost


def _execute_openai_request(prompt: str,
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

    return _execute_openai_request(prompt, model)


def _get_summarized_all(text: str,
                        model: str
                        ) -> dict:
    """Generate a summary from a concatenated summary string."""

    prompt = (f"Write a detailed synopsis based on the following notes. "
              f"Only answer truthfully and don't include anything "
              f"not in the original summary: "
              f"\n\n>>>> START OF INTERVIEW NOTES \n\n{text} \n\n>>>>"
              f"END OF INTERVIEW NOTES \n\nSynopsis:")

    return _execute_openai_request(prompt, model)


def _get_concise_chunk(text: str,
                       model: str,
                       max_examples: int = 1
                       )-> dict:
    """Generate a concise transcript for a given chunk."""

    prompt = (f"The following are sections of an interview transcript. "
              f"Please clean it up but still in dialogue form. The speaker "
              f"name should always be preserved. Do not add any details "
              f"not present in the original transcript. ")

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

    return _execute_openai_request(prompt, model)


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
    """Chunk up the transcript and generate concise transcripts for each chunk."""
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


@shared_task
def generate_synthesis(transcript_id):
    """Generate an AI-synthesized summary for a transcript."""
    tct = Transcript.objects.get(id=transcript_id)
    chunks = _generate_chunks(tct)

    summary_chunks = _process_chunks_for_summaries(tct, chunks)
    _generate_summary(tct, summary_chunks)

    concise_chunks = _process_chunks_for_concise(tct, chunks)
    _generate_concise(tct, concise_chunks)
