import requests
from app.settings import SYNTHESIS_CORE_BASE_URL


def save_transcript_for_id(transcript_id: int, transcript: str):
    """Saves the transcript on the synthesis service."""
    response = requests.post(
        f"{SYNTHESIS_CORE_BASE_URL}/transcript/{transcript_id}",
        data=transcript,
        headers={'Content-Type': 'text/plain'})
    if response.status_code != 204:
        print(
            f"Could not save transcript with {transcript_id}"
            " on synthesis service")
    else:
        print(
            f"Saved transcript {transcript_id} successfully"
            " on synthesis service")


def delete_transcript_for_id(transcript_id: int):
    """Deletes the transcript on the synthesis service."""
    response = requests.delete(
        f"{SYNTHESIS_CORE_BASE_URL}/transcript/{transcript_id}")
    if 200 <= response.status_code and response:
        print(
            f"Could not delete transcript with {transcript_id}"
            " on synthesis service")
    else:
        print(
            f"Deleted transcript {transcript_id} successfully"
            " on synthesis service")


def get_summary_with_reverse_lookup(transcript_id: int, interviewee: str):
    """Gets the summary for the transcript from the synthesis service."""
    url = "{}/transcript/{}/summary?interviewee={}".format(
        SYNTHESIS_CORE_BASE_URL, transcript_id, interviewee)
    response = requests.get(url=url)
    if response.status_code != 200:
        print(
            "Summary generation failed for transcript"
            f" with id = {transcript_id}")
    else:
        return response.json()


def get_concise_with_reverse_lookup(transcript_id: int, interviewee: str):
    """Gets the concise transcript from the synthesis service."""
    url = "{}/transcript/{}/concise?interviewee={}".format(
        SYNTHESIS_CORE_BASE_URL, transcript_id, interviewee)
    response = requests.get(url=url)
    if response.status_code != 200:
        print(
            "Concise generation failed for transcript"
            f" with id = {transcript_id}")
    else:
        return response.json()
