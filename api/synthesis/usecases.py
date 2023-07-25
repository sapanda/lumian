from typing import List
from .domains import (
    CitationResult, SynthesisResult, EmbedsResult, SynthesisResponse
)
from .errors import ObjectNotFoundException, ObjectAlreadyPresentException
from .interfaces import SynthesisInterface
from .models import ProcessedTranscript
from .server import get_synthesis
from .utils import split_text_into_multiple_lines_for_speaker
from core.models import AppSettings
from transcript.models import Transcript


def _get_transcript(tct: Transcript) -> ProcessedTranscript:
    """Return the transcript from storage"""
    try:
        ptranscript = ProcessedTranscript.objects.get(transcript=tct)
    except ProcessedTranscript.DoesNotExist:
        raise ObjectNotFoundException(
            detail=f"Transcript for id = {id} not found")
    return ptranscript


def process_transcript(tct: Transcript) -> None:
    """Generate a multiline transcript with index references in the original
    transcript text and save it in storage"""
    ptranscripts = ProcessedTranscript.objects.filter(transcript=tct)
    if len(ptranscripts) == 0:
        data = split_text_into_multiple_lines_for_speaker(
            tct.transcript, AppSettings.get().indexed_line_min_chars)
        ProcessedTranscript.objects.create(transcript=tct, data=data)
    else:
        raise ObjectAlreadyPresentException(
            detail=f"Transcript for id = {id} is already"
            "present in storage")


def _synthesis_to_citation_result(sresults: SynthesisResult,
                                  transcript_data: List[dict]
                                  ) -> CitationResult:
    citations = []
    for text_reference in sresults["output"]:
        text = text_reference["text"]
        references = []
        for num in text_reference['references']:
            references.append([transcript_data[num]["start"],
                               transcript_data[num]["end"]])
        citations.append({
            'text': text,
            'references': references
        })
    retval: CitationResult = {
        'output': citations,
        'prompt': sresults['prompt'],
        'cost': sresults['cost']
    }
    return retval


def get_transcript_summary(
        tct: Transcript, synthesis: SynthesisInterface = get_synthesis()
) -> SynthesisResponse:
    """Generate a summary from the transcript"""
    ptct = _get_transcript(tct)
    # TODO: add support for multiple interviewees
    results = synthesis.summarize_transcript(
        ptct.indexed, tct.interviewee_names[0])
    synthesis_results = _synthesis_to_citation_result(results, ptct.data)
    synthesis_results['metadata'] = results['metadata']
    return synthesis_results


def get_transcript_concise(
        tct: Transcript, synthesis: SynthesisInterface = get_synthesis()
) -> CitationResult:
    """Generate a concise transcript from the transcript"""
    ptct = _get_transcript(tct)
    # TODO: add support for multiple interviewees
    results = synthesis.concise_transcript(
        ptct.indexed, tct.interviewee_names[0])
    return _synthesis_to_citation_result(results, ptct.data)


def create_transcript_embeds(
        tct: Transcript, synthesis: SynthesisInterface = get_synthesis()
) -> EmbedsResult:
    """Generate embeds from the transcript"""
    ptct = _get_transcript(tct)
    # TODO: add support for multiple interviewees
    return synthesis.embed_transcript(
        transcript_id=tct.id,
        transcript_title=tct.title,
        indexed_transcript=ptct.indexed,
        interviewee=tct.interviewee_names[0])


def run_transcript_query(
        tct: Transcript,
        query: str,
        synthesis: SynthesisInterface = get_synthesis()
) -> CitationResult:
    """Run query against the transcript"""
    ptct = _get_transcript(tct)
    results = synthesis.query_transcript(tct.id, query)
    return _synthesis_to_citation_result(results, ptct.data)
