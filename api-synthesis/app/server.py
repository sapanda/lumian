from fastapi import (
    FastAPI, Depends, status, Body, Response
)
import json
from sqlalchemy.orm import Session

from . import models, usecases
from .config import Settings
from .database import SessionLocal, engine
from .errors import (
    OpenAITimeoutException, ObjectNotFoundException, SynthesisAPIException,
    ObjectAlreadyPresentException
)
from .interfaces import (
    OpenAIClientInterface, EmbedsClientInterface,
    TranscriptRepositoryInterface, SynthesisInterface
)
from .openai_client import OpenAIClient
from .pinecone_client import PineconeClient
from .repositories import TranscriptRepository
from .synthesis import Synthesis


EXCEPTION_TO_STATUS_CODE_MAPPING = {
    ObjectAlreadyPresentException: status.HTTP_409_CONFLICT,
    ObjectNotFoundException: status.HTTP_404_NOT_FOUND,
    OpenAITimeoutException: status.HTTP_500_INTERNAL_SERVER_ERROR
}

settings = Settings()

# Use for attaching VSCode debugger
if settings.debug:
    import debugpy
    debugpy.listen(("0.0.0.0", 3001))

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Synthesis API",
    version="0.0.1"
)


def get_settings():
    """Settings provider"""
    return settings


def get_db() -> Session:
    """DB connection provider"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_transcript_repo(
    db: Session = Depends(get_db)
) -> TranscriptRepositoryInterface:
    """Transcript Repository provider"""
    return TranscriptRepository(session=db)


def get_openai_client(
    settings: Settings = Depends(get_settings)
) -> OpenAIClientInterface:
    """OpenAI client provider"""
    return OpenAIClient(
        org_id=settings.openai_org_id,
        api_key=settings.openai_api_key
    )


def get_embeds_client(
    settings: Settings = Depends(get_settings)
) -> EmbedsClientInterface:
    """Embeds client provider"""

    if settings.pinecone_user:
        namespace = f'dev-{settings.pinecone_user}'
    else:
        namespace = 'dev'

    return PineconeClient(
        api_key=settings.pinecone_api_key,
        index_name=settings.pinecone_index,
        region=settings.pinecone_region,
        dimensions=settings.pinecone_dimensions,
        namespace=namespace
    )


def get_synthesis(
    settings: Settings = Depends(get_settings),
    openai_client: OpenAIClientInterface = Depends(get_openai_client),
    embeds_client: EmbedsClientInterface = Depends(get_embeds_client)
) -> SynthesisInterface:
    """Synthesis instance provider"""
    return Synthesis(
        openai_client=openai_client,
        embeds_client=embeds_client,
        chunk_min_words=settings.chunk_min_words,
        context_max_chars=settings.context_max_chars,
        examples_dir=settings.examples_dir)


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
    data = usecases.get_transcript(id, repo)
    return data


@app.post('/transcript/{id}')
def save_transcript(
    id: int,
    settings: Settings = Depends(get_settings),
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
    transcript: str = Body(),
):
    """API for saving a transcript"""
    usecases.save_transcript(id=id, transcript=transcript,
                             line_min_size=settings.line_min_size, repo=repo)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete('/transcript/{id}')
def delete_transcript(
    id: int,
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
    embeds_client: EmbedsClientInterface = Depends(get_embeds_client)
):
    """API for deleting a transcript"""
    usecases.delete_transcript(id, repo)
    embeds_client.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get('/transcript/{id}/summary')
def get_transcript_summary(
    id: int,
    interviewee: str,
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
    synthesis: Synthesis = Depends(get_synthesis)
):
    """API for getting a summary of a transcript"""
    results = usecases.get_transcript_summary(
        id=id,
        interviewee=interviewee,
        repo=repo,
        synthesis=synthesis
    )
    return results


@app.get('/transcript/{id}/concise')
def get_transcript_concise(
    id: int,
    interviewee: str,
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
    synthesis: Synthesis = Depends(get_synthesis)
):
    """API for getting a concise transcript"""
    results = usecases.get_transcript_concise(
        id=id,
        interviewee=interviewee,
        repo=repo,
        synthesis=synthesis
    )
    return results


@app.post('/transcript/{id}/embeds')
def create_transcript_embeds(
    id: int,
    title: str,
    interviewee: str,
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
    synthesis: Synthesis = Depends(get_synthesis)
):
    """API for generating vecotr embeds for a transcript"""
    results = usecases.create_transcript_embeds(
        id=id,
        title=title,
        interviewee=interviewee,
        repo=repo,
        synthesis=synthesis
    )
    return results


@app.post('/transcript/{id}/query')
def run_transcript_query(
    id: int,
    ask: str,
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
    synthesis: Synthesis = Depends(get_synthesis)
):
    """API for running a query against a transcript"""
    results = usecases.run_transcript_query(
        id=id,
        query=ask,
        repo=repo,
        synthesis=synthesis
    )
    return results