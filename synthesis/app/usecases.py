from .domains import Transcript, SummaryResult
from .errors import ObjectNotFoundException, ObjectAlreadyPresentException
from .interfaces import TranscriptRepositoryInterface, SynthesisInterface
from .utils import split_text_into_multiple_lines_for_speaker


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
    """Generate a multiline transcript with index references in the original
    transcript text and save it in storage"""
    transcript = repo.get(id=id)
    if not transcript:
        raise ObjectNotFoundException(
            detail=f"Transcript for id = {id} not found")
    return transcript.data


def delete_transcript(
        id: int,
        repo: TranscriptRepositoryInterface):
    """Delete a saved transcript from storage"""
    transcript = repo.get(id=id)
    if not transcript:
        raise ObjectNotFoundException(
            detail=f"Transcript for id = {id} not found")
    repo.delete(id=id)


def get_transcript_summary(
        id: int,
        interviewee: str,
        repo: TranscriptRepositoryInterface,
        synthesis: SynthesisInterface) -> SummaryResult:
    transcript = repo.get(id=id)
    if not transcript:
        raise ObjectNotFoundException(
            detail=f"Transcript for id = {id} not found")
    data = transcript.data
    results = synthesis.summarize_transcript(
        str(transcript), interviewee)
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
