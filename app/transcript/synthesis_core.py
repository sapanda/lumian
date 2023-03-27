import requests, os
from app.settings import SYNTHESIS_CORE_BASE_URL

def save_transcript_for_id(transcript_id: int, transcript : str):
    print("synthesis_core_url: ",SYNTHESIS_CORE_BASE_URL)
    try:
        requests.post(f"{SYNTHESIS_CORE_BASE_URL}/transcript/{transcript_id}", data=transcript, headers={'Content-Type': 'text/plain'})
    except Exception as e:
        print(e)

def get_summary_with_reverse_lookup(transcript_id: int, interviewee: str):
    response = requests.get(f"{SYNTHESIS_CORE_BASE_URL}/transcript/{transcript_id}/summary?interviewee={interviewee}")
    return response.json()

def delete_transcript_for_id(transcript_id: int):
    try:
        requests.delete(f"{SYNTHESIS_CORE_BASE_URL}/transcript/{transcript_id}")
    except Exception as e:
        print(e)