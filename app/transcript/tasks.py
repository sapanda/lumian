from celery import shared_task
from django.conf import settings
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


def _execute_openai_request(prompt: str, model: str) -> dict:
    """Execute an OpenAI API request and return the response."""

    COMPLETIONS_API_PARAMS = {
        "temperature": DEFAULT_TEMPERATURE,
        "max_tokens": DEFAULT_MAX_TOKENS,
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
        "summary": summary,
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


def _process_chunks(tct: Transcript) -> AIChunks:
    """Chunk up the transcript and generate summaries for each chunk."""
    interviewee = tct.interviewee_names[0]  # Support one interviewee for now
    model = OPENAI_MODEL_CHAT

    paragraph_groups = chunk_by_paragraph_groups(
        tct.transcript,
        interviewee,
    )

    summaries = []
    tokens_used = []
    for group in paragraph_groups:
        response = _get_summarized_chunk(group, model, interviewee)
        summaries.append(response['summary'])
        tokens_used.append(response['tokens_used'])

    chunks = AIChunks.objects.create(
        transcript=tct,
        chunk_type=SynthesisType.SUMMARY,
        chunks=paragraph_groups,
        chunks_processed=summaries,
        tokens_used=tokens_used,
        cost=_calculate_cost(sum(tokens_used), model),
        model_name=model,
    )
    chunks.save()
    return chunks


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
        output=response['summary'],
        tokens_used=response['tokens_used'],
        total_cost=total_cost,
        model_name=model,
    )
    summary_obj.save()
    return summary_obj


@shared_task
def generate_summary(transcript_id):
    """Generate an AI-synthesized summary for a transcript."""
    tct = Transcript.objects.get(id=transcript_id)
    chunks = _process_chunks(tct)
    _generate_summary(tct, chunks)
