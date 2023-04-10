import json
import time

import psycopg2
from psycopg2._psycopg import connection

from fastapi import (
    FastAPI, Depends, status, Body, Response
)

from .config import Settings
from .interfaces import (
    TranscriptRepositoryInterface, OpenAIClientInterface, SynthesisInterface
)
from .openai_client import OpenAIClient
from .repositories import TranscriptRepository
from .synthesis import Synthesis
from .errors import (
    OpenAITimeoutException, ObjectNotFoundException, SynthesisAPIException,
    ObjectAlreadyPresentException
)
from .usecases import (
    save_transcript as _save_transcript,
    delete_transcript as _delete_transcript,
    get_transcript_summary as _get_transcript_summary,
    get_transcript as _get_transcript
)


settings = Settings()
retry_db_con = 0
while retry_db_con < 5:
    try:
        # TODO: do something on connection failure
        postgres_connection = psycopg2.connect(
            user=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name)
        break
    except Exception:
        retry_db_con += 1
        time.sleep(2)

EXCEPTION_TO_STATUS_CODE_MAPPING = {
    ObjectAlreadyPresentException: status.HTTP_409_CONFLICT,
    ObjectNotFoundException: status.HTTP_404_NOT_FOUND,
    OpenAITimeoutException: status.HTTP_500_INTERNAL_SERVER_ERROR
}


def get_settings():
    """Settings provider"""
    return settings


def get_db_connection(
    settings: Settings = Depends(get_settings)
) -> connection:
    """DB connection provider"""
    return postgres_connection


def get_transcript_repo(
    conn: connection = Depends(get_db_connection)
) -> TranscriptRepositoryInterface:
    """Transcript Repository provider"""
    return TranscriptRepository(conn=conn)


def get_openai_client(
    settings: Settings = Depends(get_settings)
) -> OpenAIClientInterface:
    """OpenAI client provider"""
    return OpenAIClient(
        org_id=settings.openai_org_id,
        api_key=settings.openai_api_key
    )


def get_synthesis(
    settings: Settings = Depends(get_settings),
    openai_client: OpenAIClientInterface = Depends(get_openai_client)
) -> SynthesisInterface:
    """Synthesis instance provider"""
    return Synthesis(
        openai_client=openai_client,
        max_summary_size=settings.max_summary_size,
        chunk_min_words=settings.chunk_min_words,
        examples_file=settings.examples_file)


app = FastAPI(
    title="Synthesis API",
    version="0.0.1"
)


@app.exception_handler(SynthesisAPIException)
def exception_handler(request, exc: SynthesisAPIException):
    """Exception handler for OpenAITimeoutException"""
    status_code = EXCEPTION_TO_STATUS_CODE_MAPPING[type(exc)]
    return Response(content=json.dumps({"error": exc.detail}),
                    status_code=status_code)


@app.get('/transcript/{id}')
def get_transcript(
    id: int,
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
):
    """API for getting a transcript the way it is stored"""
    data = _get_transcript(id=id, repo=repo)
    return data


@app.post('/transcript/{id}')
def save_transcript(
    id: int,
    settings: Settings = Depends(get_settings),
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
    transcript: str = Body(),
):
    """API for saving a transcript"""
    _save_transcript(id=id, transcript=transcript,
                     line_min_size=settings.line_min_size, repo=repo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete('/transcript/{id}')
def delete_transcript(
    id: int,
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo)
):
    """API for deleting a transcript"""
    _delete_transcript(id=id, repo=repo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get('/transcript/{id}/summary')
def get_transcript_summary(
    id: int,
    interviewee: str,
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
    synthesis: Synthesis = Depends(get_synthesis)
):
    """API for getting a summary of a transcript"""
    results = _get_transcript_summary(
        id=id,
        interviewee=interviewee,
        repo=repo,
        synthesis=synthesis
    )
    return results
