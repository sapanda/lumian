from celery import shared_task
from django.conf import settings
import openai

from transcript.models import Transcript, AISynthesis, ProcessedChunks
from transcript.ai.utils import chunk_by_paragraph_groups


# Open AI models and pricing (USD per 1k tokens)
OPENAI_COMPLETIONS_MODEL = "text-davinci-003"
OPENAI_COMPLETIONS_PRICE = 0.002

OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
OPENAI_EMBEDDING_PRICE = 0.0004

# Engineering Params
CHUNK_MIN_SIZE = 150
TOKEN_CUT_OFF = 2000

# Model Params
DEFAULT_TEMPERATURE = 0
MAX_TOKENS_IN_RESPONSE = 600

COMPLETIONS_API_PARAMS = {
    "temperature": DEFAULT_TEMPERATURE,
    "max_tokens": MAX_TOKENS_IN_RESPONSE,
    "model": OPENAI_COMPLETIONS_MODEL,
}

openai.organization = settings.OPENAI_ORG_ID
openai.api_key = settings.OPENAI_API_KEY


def _get_summarized_chunk(text: str, interviewee: str = None) -> dict:
    """Generate a summary for a chunk of the transcript."""

    if interviewee is not None:
        prompter = "detailed summary of only {interviewee}'s comments"
    else:
        prompter = "summary"

    prompt = (f"The following is a section of an interview transcript. "
              f"Please provide a {prompter}. Only answer truthfully and "
              f"don't include anything not in the original transcript: "
              f"\n\n>>>> START OF INTERVIEW \n\n{text}\n\n"
              f">>>> END OF INTERVIEW \n\n"
              f"Detailed Summary: ")

    response = openai.Completion.create(
                prompt=prompt,
                **COMPLETIONS_API_PARAMS
            )

    ret_val = {
        'summary': response["choices"][0]["text"].strip(" \n"),
        'tokens_used': response["usage"]["total_tokens"],
    }

    return ret_val


def _get_summarized_all(text: str) -> dict:
    """Generate a summary from a concatenated summary string."""

    prompt = (f"Write a detailed synopsis based on the following notes. "
              f"Only answer truthfully and don't include anything "
              f"not in the original summary: "
              f"\n\n>>>> START OF INTERVIEW NOTES \n\n{text} \n\n>>>>"
              f"END OF INTERVIEW NOTES \n\nSynopsis:")

    response = openai.Completion.create(
                prompt=prompt,
                **COMPLETIONS_API_PARAMS
            )

    ret_val = {
        'summary': response["choices"][0]["text"].strip(" \n"),
        'tokens_used': response["usage"]["total_tokens"],
    }

    return ret_val


def _process_chunks(tct: Transcript) -> Transcript:
    """Chunk up the transcript and generate summaries for each chunk."""
    interviewee = tct.interviewee_names[0]  # Support one interviewee for now

    paragraph_groups = chunk_by_paragraph_groups(
        tct.transcript,
        interviewee,
    )

    summaries = []
    tokens_used = []
    for group in paragraph_groups:
        response = _get_summarized_chunk(group, interviewee)
        summaries.append(response['summary'])
        tokens_used.append(response['tokens_used'])

    tct.chunks = ProcessedChunks.objects.create(
        para_groups=paragraph_groups,
        para_group_summaries=summaries,
        tokens_used=tokens_used,
    )
    return tct


def _generate_summary(tct: Transcript) -> Transcript:
    """Generate the AISynthesis summary for the transcript."""
    concat_summary = " ".join(tct.chunks.para_group_summaries)
    response = _get_summarized_all(concat_summary)

    tct.summary = AISynthesis.objects.create(
        output_type=AISynthesis.SynthesisType.SUMMARY,
        output=response['summary'],
        tokens_used=response['tokens_used'],
    )
    return tct


def _calculate_cost(tct: Transcript) -> Transcript:
    """Calculate the cost of the transcript."""
    tokens_used = sum(tct.chunks.tokens_used) + tct.summary.tokens_used
    tct.summary_cost = tokens_used * OPENAI_COMPLETIONS_PRICE / 1000
    return tct


@shared_task
def generate_summary(transcript_id):
    """Generate an AI-synthesized summary for a transcript."""
    tct = Transcript.objects.get(id=transcript_id)
    tct = _process_chunks(tct)
    tct = _generate_summary(tct)
    tct = _calculate_cost(tct)
    tct.save()
