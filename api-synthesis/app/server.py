from fastapi import (
    FastAPI, Depends, status, Body, Request, Response
)
from fastapi.responses import JSONResponse
import json
import logging
from sqlalchemy.orm import Session

from . import models, usecases
from .config import Settings, ModeEnum
from .database import SessionLocal, engine
from .errors import (
    OpenAITimeoutException, OpenAIRateLimitException,
    ObjectNotFoundException, SynthesisAPIException,
    ObjectAlreadyPresentException, PineconeException,
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
    OpenAITimeoutException: status.HTTP_500_INTERNAL_SERVER_ERROR,
    OpenAIRateLimitException: status.HTTP_500_INTERNAL_SERVER_ERROR,
    PineconeException: status.HTTP_500_INTERNAL_SERVER_ERROR,
}

settings = Settings()
openai_client = None
embeds_client = None

# Use for attaching VSCode debugger
if settings.deploy_mode == ModeEnum.local and settings.debug:
    import debugpy
    debugpy.listen(("0.0.0.0", 3001))

if settings.deploy_mode == ModeEnum.development or \
   settings.deploy_mode == ModeEnum.production:
    import sentry_sdk
    sentry_sdk.init(
        dsn=settings.sentry_dsn,

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=1.0,
    )

LOG_FORMAT = "[%(levelname)s] %(message)s | %(filename)s %(funcName)s() Line %(lineno)d"  # noqa
LOG_LEVEL = logging.getLevelName(settings.synthesis_log_level)
logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
logger = logging.getLogger(__name__)

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
    global openai_client
    if openai_client is None:
        openai_client = OpenAIClient(
            completions_api_type=settings.openai_completions_api_type,
            completions_api_key=settings.openai_completions_api_key,
            completions_api_base=settings.openai_completions_api_base,
            completions_api_version=settings.openai_completions_api_version,
            completions_model=settings.openai_completions_model,
            embeddings_api_type=settings.openai_embeddings_api_type,
            embeddings_api_key=settings.openai_embeddings_api_key,
            embeddings_api_base=settings.openai_embeddings_api_base,
            embeddings_api_version=settings.openai_embeddings_api_version,
            embeddings_model=settings.openai_embeddings_model,
        )
    return openai_client


def get_embeds_client(
    settings: Settings = Depends(get_settings)
) -> EmbedsClientInterface:
    """Embeds client provider"""

    if settings.pinecone_user:
        namespace = f'dev-{settings.pinecone_user}'
    else:
        namespace = 'dev'

    global embeds_client
    if embeds_client is None:
        embeds_client = PineconeClient(
            api_key=settings.pinecone_api_key,
            index_name=settings.pinecone_index,
            region=settings.pinecone_region,
            dimensions=settings.pinecone_dimensions,
            namespace=namespace
        )
    return embeds_client


def get_synthesis(
    settings: Settings = Depends(get_settings),
    openai_client: OpenAIClientInterface = Depends(get_openai_client),
    embeds_client: EmbedsClientInterface = Depends(get_embeds_client)
) -> SynthesisInterface:
    """Synthesis instance provider"""
    return Synthesis(
        openai_client=openai_client,
        embeds_client=embeds_client,
        chunk_min_tokens_summary=settings.chunk_min_tokens_summary,
        chunk_min_tokens_concise=settings.chunk_min_tokens_concise,
        chunk_min_tokens_query=settings.chunk_min_tokens_query,
        max_input_tokens_summary=settings.max_input_tokens_summary,
        max_input_tokens_concise=settings.max_input_tokens_concise,
        max_input_tokens_query=settings.max_input_tokens_query,
        max_input_tokens_metadata=settings.max_input_tokens_metadata
    )


@app.exception_handler(SynthesisAPIException)
def exception_handler(request, exc: SynthesisAPIException):
    """Exception handler for SynthesisAPIException"""
    status_code = EXCEPTION_TO_STATUS_CODE_MAPPING[type(exc)]
    return Response(content=json.dumps({"error": exc.detail}),
                    status_code=status_code)


if settings.debug:
    @app.middleware("http")
    async def log_internal_server_errors(request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception as e:
            logger.exception("Internal server error", exc_info=e)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
        return response


@app.get('/transcript/{id}')
def get_transcript(
    id: int,
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
):
    logger.info(f" ---- GET request initiated :  /transcript/{id}")
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
    logger.info(f" ---- POST request initiated :  /transcript/{id}")
    """API for saving a transcript"""
    usecases.save_transcript(id=id, transcript=transcript,
                             line_min_chars=settings.indexed_line_min_chars,
                             repo=repo)
    return Response(status_code=status.HTTP_201_CREATED)


@app.delete('/transcript/{id}')
def delete_transcript(
    id: int,
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
    embeds_client: EmbedsClientInterface = Depends(get_embeds_client)
):
    logger.info(f" ---- DELETE request initiated :  /transcript/{id}")
    """API for deleting a transcript"""
    usecases.delete_transcript(id, repo)
    embeds_client.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get('/transcript/{id}/metadata')
def get_transcript_metadata(
    id: int,
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
    synthesis: Synthesis = Depends(get_synthesis)
):
    logger.info(f" ---- GET request initiated :  /transcript/{id}/metadata")
    """
        API for getting metadata of a meeting transcript :
        Metadata : (title, interviewee, interviwerrs)
    """
    results = usecases.get_transcript_metadata(
        id=id,
        repo=repo,
        synthesis=synthesis
    )
    return results


@app.get('/transcript/{id}/summary')
def get_transcript_summary(
    id: int,
    interviewee: str,
    repo: TranscriptRepositoryInterface = Depends(get_transcript_repo),
    synthesis: Synthesis = Depends(get_synthesis)
):
    logger.info(f" ---- GET request initiated :  /transcript/{id}/summary")
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
    logger.info(f" ---- GET request initiated :  /transcript/{id}/concise")
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
    logger.info(f" ---- POST request initiated :  /transcript/{id}/embeds")
    """API for generating vector embeds for a transcript"""
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
    logger.info(f" ---- POST request initiated :  /transcript/{id}/query")
    """API for running a query against a transcript"""
    results = usecases.run_transcript_query(
        id=id,
        query=ask,
        repo=repo,
        synthesis=synthesis
    )
    return results
