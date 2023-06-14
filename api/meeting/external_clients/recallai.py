import requests
from retry import retry
from urllib.parse import urlencode
import datetime
from requests.exceptions import (
    HTTPError,
    RequestException
)
from meeting.errors import RecallAITimeoutException
from app.settings import (
    RECALL_API_KEY,
    RECALL_TRANSCRIPT_PROVIDER,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URL
)
import logging
logger = logging.getLogger(__name__)

CREATE_BOT_URL = "https://api.recall.ai/api/v1/bot/"
MEETING_TRANSCRIPT_URL = "https://api.recall.ai/api/v1/bot/{}/transcript/"
CREATE_CALENDAR_URL = "https://api.recall.ai/api/v2/calendars/"
RETRIEVE_CALENDAR_URL = "https://api.recall.ai/api/v2/calendars/{}/"
LIST_CALENDAR_EVENTS = "https://api.recall.ai/api/v2/calendar-events/"


@retry(RecallAITimeoutException, tries=3, delay=5, backoff=2)
def add_bot_to_meeting(bot_name: str, meeting_url: str, join_at: str = None):

    url = CREATE_BOT_URL
    token = RECALL_API_KEY
    transcript_provider = RECALL_TRANSCRIPT_PROVIDER

    payload = {
        "bot_name": bot_name,
        "transcription_options": {"provider": transcript_provider},
        "meeting_url": meeting_url,
        "join_at": join_at if join_at else None
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
    except HTTPError as e:
        error_msg = f"HTTP error occurred: {e}"
        status_code = e.response.status_code
        raise RecallAITimeoutException(error_msg, status_code)
    except RequestException as e:
        error_msg = f"An error occurred: {e}"
        status_code = None
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
    except HTTPError as e:
        error_msg = f"HTTP error occurred: {e}"
        status_code = e.response.status_code
        raise RecallAITimeoutException(error_msg, status_code)
    except RequestException as e:
        error_msg = f"An error occurred: {e}"
        status_code = None
        raise RecallAITimeoutException(error_msg, status_code)


@retry(RecallAITimeoutException, tries=3, delay=5, backoff=2)
def create_calendar(refresh_token):

    url = CREATE_CALENDAR_URL
    token = RECALL_API_KEY

    payload = {
        "platform": "google_calendar",
        "oauth_client_id": GOOGLE_CLIENT_ID,
        "oauth_client_secret": GOOGLE_CLIENT_SECRET,
        "oauth_refresh_token": refresh_token,
        "webhook_url": GOOGLE_REDIRECT_URL
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Token " + token
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        res = response.json()
        return res['id']
    except HTTPError as e:
        error_msg = f"HTTP error occurred: {e}"
        status_code = e.response.status_code
        raise RecallAITimeoutException(error_msg, status_code)
    except RequestException as e:
        error_msg = f"An error occurred: {e}"
        status_code = None
        raise RecallAITimeoutException(error_msg, status_code)


@retry(RecallAITimeoutException, tries=3, delay=10, backoff=3)
def retrieve_calendar(calendar_id):

    url = RETRIEVE_CALENDAR_URL.format(calendar_id)
    token = RECALL_API_KEY

    headers = {
        "accept": "application/json",
        "Authorization": "Token " + token
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        res = response.json()
        if not res['oauth_email']:
            raise RequestException()
        return res['oauth_email']
        # TODO : check status and fetch reason in case of error
    except HTTPError as e:
        error_msg = f"HTTP error occurred: {e}"
        status_code = e.response.status_code
        raise RecallAITimeoutException(error_msg, status_code)
    except RequestException as e:
        error_msg = f"An error occurred: {e}"
        status_code = None
        raise RecallAITimeoutException(error_msg, status_code)


@retry(RecallAITimeoutException, tries=3, delay=5, backoff=2)
def list_calendar_events(calendar_id, schedule=False):

    now = datetime.datetime.utcnow()
    if schedule:
        time_min = now.isoformat() + 'Z'
        time_max = (now + datetime.timedelta(minutes=30)).isoformat() + 'Z'
    else:
        time_min = (now - datetime.timedelta(minutes=60)).isoformat() + 'Z'
        time_max = (now + datetime.timedelta(minutes=1)).isoformat() + 'Z'
    params = {
                "start_time__gte": time_min,
                "start_time__lte": time_max,
                "calendar_id": calendar_id,
            }

    url = f"{LIST_CALENDAR_EVENTS}?{urlencode(params)}"
    token = RECALL_API_KEY

    headers = {
        "accept": "application/json",
        "Authorization": "Token " + token
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        res = response.json()
        events = []
        for result in res['results']:
            event = {}
            event['meeting_url'] = result['raw']['location']
            event['start_time'] = result['raw']['start']['dateTime']
            event['end_time'] = result['raw']['end']['dateTime']
            event['title'] = result['raw']['summary']

            # TODO : Check if meeting has been finished already
            events.append(event)

        return events
    except HTTPError as e:
        error_msg = f"HTTP error occurred: {e}"
        status_code = e.response.status_code
        raise RecallAITimeoutException(error_msg, status_code)
    except RequestException as e:
        error_msg = f"An error occurred: {e}"
        status_code = None
        raise RecallAITimeoutException(error_msg, status_code)
