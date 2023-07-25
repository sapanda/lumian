from decimal import Decimal
import logging
from rest_framework import status
from typing import List
from .models import (
    Transcript, SynthesisType, Query, Embeds, Synthesis, SynthesisStatus
)
from synthesis import usecases
from synthesis.errors import (
    ObjectNotFoundException, ObjectAlreadyPresentException
)


logger = logging.getLogger(__name__)


def _create_result(status_code: status, data: dict = None) -> dict:
    """Creates a result dict from the response."""
    if data:
        return {**data, 'status_code': status_code}
    else:
        return {'status_code': status_code}


def initiate_synthesis(tct: Transcript) -> dict:
    """Initiate transcript synthesis using the synthesis module"""
    try:
        usecases.process_transcript(tct)
        code = status.HTTP_201_CREATED
    except ObjectAlreadyPresentException:
        code = status.HTTP_409_CONFLICT
    except Exception as e:
        logger.exception(e, exc_info=True)
        code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if code != status.HTTP_201_CREATED:
        logger.error(
            f"Could not save transcript with {tct.id}"
            " on synthesis service")
    return _create_result(status_code=code)


def _update_metadata_from_result(
        tct: Transcript, result: dict) -> None:
    """Generate the metadata for the transcript."""
    result = result['metadata']
    if result.get("title"):
        tct.title = result["title"]
    if result.get("interviewees"):
        tct.interviewee_names = result["interviewees"]
    if result.get("interviewers"):
        tct.interviewer_names = result["interviewers"]
    tct.metadata_generated = True
    tct.cost += Decimal(result["cost"])
    tct.save()


def _update_synthesis_from_result(tct: Transcript,
                                  synthesis: Synthesis,
                                  result: dict) -> None:
    """Create a synthesis object from the result of a synthesis request."""
    synthesis.output = result["output"]
    synthesis.prompt = result["prompt"]
    synthesis.cost = Decimal(result["cost"])
    synthesis.status = SynthesisStatus.COMPLETED
    synthesis.save()

    tct.cost += synthesis.cost
    tct.save()


def _mark_synthesis_as_failed(synthesis: Synthesis) -> None:
    """Mark the synthesis as failed."""
    synthesis.status = SynthesisStatus.FAILED
    synthesis.save()


def _mark_embeds_as_failed(embeds: Embeds) -> None:
    """Mark the synthesis as failed."""
    embeds.status = SynthesisStatus.FAILED
    embeds.save()


def generate_summary(tct: Transcript) -> dict:
    """Generate synthesized summary using the synthesis module"""
    try:
        synthesis = Synthesis.objects.get(
            transcript=tct,
            output_type=SynthesisType.SUMMARY
        )

        summary = usecases.get_transcript_summary(tct)
        _update_synthesis_from_result(tct, synthesis, summary)
        _update_metadata_from_result(tct, summary)
        result = _create_result(status.HTTP_200_OK, summary)
    except ObjectNotFoundException:
        logger.exception(
            (f"Processed Transcript for Transcript={tct.id} doesn't exist. "
             f"Summary generation will be skipped."))
        _mark_synthesis_as_failed(synthesis)
        result = _create_result(status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception(
            (f"Exception on Transcript={tct.id}. "
             f"Summary generation will be skipped."),
            exc_info=e)
        _mark_synthesis_as_failed(synthesis)
        result = _create_result(status.HTTP_500_INTERNAL_SERVER_ERROR)
    return result


def generate_concise(tct: Transcript) -> dict:
    """Generate concise transcript using the synthesis service"""
    try:
        synthesis = Synthesis.objects.get(
            transcript=tct,
            output_type=SynthesisType.CONCISE
        )
        concise = usecases.get_transcript_concise(tct)
        _update_synthesis_from_result(tct, synthesis, concise)
        result = _create_result(status.HTTP_200_OK, concise)
    except ObjectNotFoundException:
        logger.error(
            (f"Processed Transcript for Transcript={tct.id} doesn't exist. "
             f"Concise generation will be skipped."))
        _mark_synthesis_as_failed(synthesis)
        result = _create_result(status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception(
            (f"Exception on Transcript={tct.id}. "
             f"Concise generation will be skipped."),
            exc_info=e)
        _mark_synthesis_as_failed(synthesis)
        result = _create_result(status.HTTP_500_INTERNAL_SERVER_ERROR)
    return result


def generate_embeds(tct: Transcript) -> dict:
    """Generate the embeds for the transcript."""
    try:
        embeds = Embeds.objects.get(transcript=tct)
        embeds_result = usecases.create_transcript_embeds(tct)
        embeds.cost = Decimal(embeds_result["cost"])
        embeds.status = SynthesisStatus.COMPLETED
        embeds.save()
        tct.cost += embeds.cost
        tct.save()
        result = _create_result(status.HTTP_200_OK, embeds_result)
    except ObjectNotFoundException:
        logger.error(
            (f"Processed Transcript for Transcript={tct.id} doesn't exist. "
             f"Concise generation will be skipped."))
        _mark_embeds_as_failed(embeds)
        result = _create_result(status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception(
            (f"Exception on Transcript={tct.id}. "
             f"Embeds generation will be skipped."),
            exc_info=e)
        _mark_embeds_as_failed(embeds)
        result = _create_result(status.HTTP_500_INTERNAL_SERVER_ERROR)
    return result


def generate_answers(tct: Transcript) -> List[dict]:
    """Generate project-level answers for the transcript."""
    questions = tct.project.questions
    query_objects = []
    for question in questions:
        try:
            query_obj = run_openai_query(
                tct, question,
                Query.QueryLevelChoices.PROJECT)
            data = {
                    'query': question,
                    'output': query_obj.output
                }
            query_objects.append(data)
        except Exception as e:
            logger.exception(f"Query : {question}", exc_info=e)
    return query_objects


def run_openai_query(tct: Transcript, query: str, level: str) -> Query:
    """Run the OpenAI query on the given transcript."""
    try:
        result = usecases.run_transcript_query(tct, query)
        query_obj = Query.objects.create(
            transcript=tct,
            query=query,
            output=result['output'],
            prompt=result["prompt"],
            cost=Decimal(result['cost']),
            query_level=level
        )
        tct.cost += query_obj.cost
        tct.save()
    except ObjectNotFoundException:
        logger.error(
            (f"Processed Transcript for Transcript={tct.id} doesn't exist. "
             f"Query will be skipped."))
        result = _create_result(status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception(
            (f"Exception on Transcript={tct.id} for query='{query}'"
             f"Query generation will be skipped."), exc_info=e)
        result = _create_result(status.HTTP_500_INTERNAL_SERVER_ERROR)
    return query_obj
