import requests
from retry import retry

from meeting.errors import RecallAITimeoutException
from app.settings import (
    RECALL_API_KEY,
    RECALL_TRANSCRIPT_PROVIDER
)

CREATE_BOT_URL = "https://api.recall.ai/api/v1/bot/"
MEETING_TRANSCRIPT_URL = "https://api.recall.ai/api/v1/bot/{}/transcript/"


@retry(RecallAITimeoutException, tries=3, delay=5, backoff=2)
def add_bot_to_meeting(bot_name: str, meeting_url: str):

    url = CREATE_BOT_URL
    token = RECALL_API_KEY
    transcript_provider = RECALL_TRANSCRIPT_PROVIDER

    payload = {
        "bot_name": bot_name,
        "transcription_options": {"provider": transcript_provider},
        "meeting_url": meeting_url
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Token " + token
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # handle HTTP errors (status code not between 200 and 299)
        error_msg = f"HTTP error occurred: {e}"
        status_code = e.response.status_code
        raise RecallAITimeoutException(error_msg, status_code)
    except requests.exceptions.RequestException as e:
        # handle other types of request exceptions (e.g. network errors)
        error_msg = f"An error occurred: {e}"
        status_code = None  # set status code to None for non-HTTP errors
        raise RecallAITimeoutException(error_msg, status_code)


@retry(RecallAITimeoutException, tries=3, delay=5, backoff=2)
def get_meeting_transcript(bot_id: str):

    url = MEETING_TRANSCRIPT_URL.format(bot_id)
    token = RECALL_API_KEY

    headers = {
        "accept": "application/json",
        "Authorization": "Token " + token
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # handle HTTP errors (status code not between 200 and 299)
        error_msg = f"HTTP error occurred: {e}"
        status_code = e.response.status_code
        raise RecallAITimeoutException(error_msg, status_code)
    except requests.exceptions.RequestException as e:
        # handle other types of request exceptions (e.g. network errors)
        error_msg = f"An error occurred: {e}"
        status_code = None  # set status code to None for non-HTTP errors
        raise RecallAITimeoutException(error_msg, status_code)
