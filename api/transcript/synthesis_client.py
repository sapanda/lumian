import requests
from urllib.parse import urlencode
from app.settings import SYNTHESIS_URL


def _create_result(response: requests.Response) -> dict:
    """Creates a result dict from the response."""
    if len(response.content) > 0:
        return {**response.json(), 'status_code': response.status_code}
    else:
        return {'status_code': response.status_code}


# TODO: Handle errors
def save_transcript_for_id(transcript_id: int,
                           transcript: str) -> dict:
    """Saves the transcript on the synthesis service."""
    response = requests.post(
        f"{SYNTHESIS_URL}/transcript/{transcript_id}",
        data=transcript,
        headers={'Content-Type': 'text/plain'})
    if response.status_code != 204:
        print(
            f"Could not save transcript with {transcript_id}"
            " on synthesis service")
    return _create_result(response)


def delete_transcript_for_id(transcript_id: int) -> dict:
    """Deletes the transcript on the synthesis service."""
    response = requests.delete(
        f"{SYNTHESIS_URL}/transcript/{transcript_id}")
    if response.status_code != 204:
        print(
            f"Could not delete transcript with {transcript_id}"
            " on synthesis service")
    return _create_result(response)


def get_summary_with_citations(transcript_id: int,
                               interviewee: str) -> dict:
    """Gets the summary for the transcript from the synthesis service."""
    query_params = {'interviewee': interviewee}
    url = "{}/transcript/{}/summary?{}".format(
        SYNTHESIS_URL, transcript_id, urlencode(query_params))
    response = requests.get(url=url)
    if response.status_code != 200:
        print(
            "Summary generation failed for transcript"
            f" with id = {transcript_id}")
    return _create_result(response)


def get_concise_with_citations(transcript_id: int,
                               interviewee: str) -> dict:
    """Gets the concise transcript from the synthesis service."""
    query_params = {'interviewee': interviewee}
    url = "{}/transcript/{}/concise?{}".format(
        SYNTHESIS_URL, transcript_id, urlencode(query_params))
    response = requests.get(url=url)
    if response.status_code != 200:
        print(
            "Concise generation failed for transcript"
            f" with id = {transcript_id}")
    return _create_result(response)


def generate_embeds(
        transcript_id: int, transcript_title: int, interviewee: str
        ) -> dict:
    """Gets the embeds for the transcript from the synthesis service."""
    query_params = {
        'interviewee': interviewee,
        'title': transcript_title
    }
    url = "{}/transcript/{}/embeds?{}".format(
        SYNTHESIS_URL, transcript_id, urlencode(query_params))
    response = requests.post(url=url)
    if response.status_code != 200:
        print(
            "Embeds generation failed for transcript"
            f" with id = {transcript_id}")
    return _create_result(response)


def run_query(transcript_id: int, query: str) -> dict:
    """Runs a query for the transcript on the synthesis service."""
    query_params = {'ask': query}
    url = "{}/transcript/{}/query?{}".format(
        SYNTHESIS_URL, transcript_id, urlencode(query_params))
    response = requests.post(url=url)
    if response.status_code != 200:
        print(
            "Running query failed for transcript"
            f" with id = {transcript_id}")
    return _create_result(response)
