import requests
from app.settings import SYNTHESIS_CORE_BASE_URL


def save_transcript_for_id(transcript_id: int, transcript: str):
    print("synthesis_core_url: ", SYNTHESIS_CORE_BASE_URL)
    try:
        requests.post(f"{SYNTHESIS_CORE_BASE_URL}/transcript/{transcript_id}",
                      data=transcript, headers={'Content-Type': 'text/plain'})
    except Exception as e:
        print(e)


def get_summary_with_reverse_lookup(transcript_id: int, interviewee: str):
    url = "{}/transcript/{}/summary?interviewee={}".format(
        SYNTHESIS_CORE_BASE_URL, transcript_id, interviewee)
    response = requests.get(url=url)
    return response.json()


def delete_transcript_for_id(transcript_id: int):
    try:
        requests.delete(
            f"{SYNTHESIS_CORE_BASE_URL}/transcript/{transcript_id}")
    except Exception as e:
        print(e)
