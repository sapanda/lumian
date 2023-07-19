import requests
import time
from retry import retry
from requests.exceptions import (
    ConnectionError,
    Timeout,
)
from rest_framework.exceptions import (
    ParseError
)
from meeting.errors import (
    AssemblyAITimeoutException
)
from django.core.files.uploadedfile import InMemoryUploadedFile
from app.settings import ASSEMBLY_API_KEY

import logging
logger = logging.getLogger(__name__)

BASE_URL = "https://api.assemblyai.com/v2"


@retry(AssemblyAITimeoutException, tries=3, delay=3, backoff=2)
def upload_file_to_assembly(file: InMemoryUploadedFile):
    headers = {
        "authorization": ASSEMBLY_API_KEY
    }
    url = BASE_URL + "/upload"
    try:
        response = requests.post(url, headers=headers, data=file)
        response.raise_for_status()
        upload_url = response.json()["upload_url"]
        return upload_url
    except (Timeout, ConnectionError) as e:
        error_msg = f"Connection error : {e}"
        status_code = e.response.status_code
        raise AssemblyAITimeoutException(error_msg, status_code)
    except Exception as e:
        error_msg = f"Error occurred: {e}"
        raise ParseError(error_msg)

@retry(AssemblyAITimeoutException, tries=3, delay=3, backoff=2)
def start_audio_transcription(upload_url: str):
    headers = {
        "authorization": ASSEMBLY_API_KEY
    }
    data = {
        "audio_url": upload_url
    }
    url = BASE_URL + "/transcript"
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()['id']
    except (Timeout, ConnectionError) as e:
        error_msg = f"Connection error : {e}"
        status_code = e.response.status_code
        raise AssemblyAITimeoutException(error_msg, status_code)
    except Exception as e:
        error_msg = f"Error occurred: {e}"
        raise ParseError(error_msg)

@retry(AssemblyAITimeoutException, tries=3, delay=3, backoff=2)
def get_audio_transcription(transcript_id: int):
    headers = {
        "authorization": ASSEMBLY_API_KEY
    }
    url = BASE_URL + "/transcript/{}"
    polling_endpoint = url.format(transcript_id)
    try:
        while True:
            transcription_result = requests.get(polling_endpoint,
                                                headers=headers).json()

            if transcription_result['status'] == 'completed':
                return transcription_result['text']

            elif transcription_result['status'] == 'error':
                raise RuntimeError(
                    f"Transcription failed: {transcription_result['error']}")

            else:
                time.sleep(3)
    except (Timeout, ConnectionError) as e:
        error_msg = f"Connection error : {e}"
        status_code = e.response.status_code
        raise AssemblyAITimeoutException(error_msg, status_code)
    except Exception as e:
        error_msg = f"Error occurred: {e}"
        raise ParseError(error_msg)


def get_transcription_for_audio(file: InMemoryUploadedFile):
    logger.info('Uploading audio to assembly server ...')
    upload_url = upload_file_to_assembly(file)
    logger.info('Starting audio transcription ...')
    transcript_id = start_audio_transcription(upload_url)
    logger.info('Waiting for transcript file ...')
    transcript = get_audio_transcription(transcript_id)

    return transcript
