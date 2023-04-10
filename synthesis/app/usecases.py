from .domains import Transcript, SummaryResult
from .errors import ObjectNotFoundException, ObjectAlreadyPresentException
from .interfaces import TranscriptRepositoryInterface, SynthesisInterface
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
        line_min_size: int,
        repo: TranscriptRepositoryInterface):
    """Generate a multiline transcript with index references in the original
    transcript text and save it in storage"""
    data = repo.get(id=id)
    if data:
        raise ObjectAlreadyPresentException(
            detail=f"Transcript for id = {id} is already"
            "present in storage")
    data = split_text_into_multiple_lines_for_speaker(
        transcript, line_min_size)
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
    _get_transcript(id, repo)  # check if transcript exists
    repo.delete(id=id)


def get_transcript_summary(
        id: int,
        interviewee: str,
        repo: TranscriptRepositoryInterface,
        synthesis: SynthesisInterface) -> SummaryResult:
    transcript = _get_transcript(id, repo)
    data = transcript.data
    results = synthesis.summarize_transcript(str(transcript), interviewee)
    final_results = []
    for text_reference in results["output"]:
        text = text_reference["text"]
        references = []
        for num in text_reference['references']:
            references.append([data[num]["start"], data[num]["end"]])
        final_results.append({
            'text': text,
            'references': references
        })
    return {'output': final_results, 'cost': results['cost']}


def get_transcript_concise(
        id: int,
        interviewee: str,
        repo: TranscriptRepositoryInterface,
        synthesis: SynthesisInterface) -> SummaryResult:
    transcript = _get_transcript(id, repo)
    data = transcript.data
    results = synthesis.concise_transcript(str(transcript), interviewee)
    final_results = []
    for text_reference in results["output"]:
        text = text_reference["text"]
        references = []
        for num in text_reference['references']:
            references.append([data[num]["start"], data[num]["end"]])
        final_results.append({
            'text': text,
            'references': references
        })
    return {'output': final_results, 'cost': results['cost']}
