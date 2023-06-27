from .domains import (
    Transcript, CitationResult, SynthesisResult, EmbedsResult,
    SynthesisResponse
)
from .errors import ObjectNotFoundException, ObjectAlreadyPresentException
from .interfaces import (
    TranscriptRepositoryInterface, SynthesisInterface
)
from .utils import split_text_into_multiple_lines_for_speaker


def _get_transcript(
        id: int,
        repo: TranscriptRepositoryInterface
) -> Transcript:
    """Return the transcript from storage"""
    transcript = repo.get(id=id)
    if not transcript:
        raise ObjectNotFoundException(
            detail=f"Transcript for id = {id} not found")
    return transcript


def save_transcript(
        id: int,
        transcript: str,
        line_min_chars: int,
        repo: TranscriptRepositoryInterface):
    """Generate a multiline transcript with index references in the original
    transcript text and save it in storage"""
    data = repo.get(id=id)
    if data:
        raise ObjectAlreadyPresentException(
            detail=f"Transcript for id = {id} is already"
            "present in storage")
    data = split_text_into_multiple_lines_for_speaker(
        transcript, line_min_chars)
    repo.save(transcript=Transcript(id=id, data=data))


def get_transcript(
        id: int,
        repo: TranscriptRepositoryInterface) -> dict:
    """Return the transcript from storage"""
    return _get_transcript(id, repo).data


def delete_transcript(
        id: int,
        repo: TranscriptRepositoryInterface):
    """Delete a saved transcript from storage"""
    _get_transcript(id, repo)  # verify transcript exists
    repo.delete(id=id)


def _synthesis_to_citation_result(sresults: SynthesisResult,
                                  transcript_data: 'list[dict]'
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
        id: int,
        interviewee: str,
        repo: TranscriptRepositoryInterface,
        synthesis: SynthesisInterface) -> SynthesisResponse:
    """Generate a summary from the transcript"""
    transcript = _get_transcript(id, repo)
    data = transcript.data
    results = synthesis.summarize_transcript(str(transcript), interviewee)
    synthesis_results = _synthesis_to_citation_result(results, data)
    synthesis_results['metadata'] = results['metadata']
    return synthesis_results


def get_transcript_concise(
        id: int,
        interviewee: str,
        repo: TranscriptRepositoryInterface,
        synthesis: SynthesisInterface) -> CitationResult:
    """Generate a concise transcript from the transcript"""
    transcript = _get_transcript(id, repo)
    data = transcript.data
    results = synthesis.concise_transcript(str(transcript), interviewee)
    return _synthesis_to_citation_result(results, data)


def create_transcript_embeds(
        id: int,
        title: str,
        interviewee: str,
        repo: TranscriptRepositoryInterface,
        synthesis: SynthesisInterface) -> EmbedsResult:
    """Generate embeds from the transcript"""
    transcript = _get_transcript(id, repo)
    return synthesis.embed_transcript(
        transcript_id=id,
        transcript_title=title,
        indexed_transcript=str(transcript),
        interviewee=interviewee
    )


def run_transcript_query(
        id: int,
        query: str,
        repo: TranscriptRepositoryInterface,
        synthesis: SynthesisInterface) -> CitationResult:
    """Run query against the transcript"""
    transcript = _get_transcript(id, repo)
    data = transcript.data
    results = synthesis.query_transcript(id, query)
    return _synthesis_to_citation_result(results, data)
