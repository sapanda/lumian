from decimal import Decimal
import logging
from . import synthesis_client
from .models import (
    Transcript, SynthesisType, Query, Embeds, Synthesis, SynthesisStatus
)


logger = logging.getLogger(__name__)


def initiate_synthesis(tct: Transcript) -> dict:
    """Initiate transcript synthesis using the synthesis service"""
    return synthesis_client.save_transcript_for_id(
        transcript_id=tct.id, transcript=tct.transcript)


def generate_metadata(tct: Transcript) -> dict:
    """Generate the metadata for the transcript."""
    result = synthesis_client.get_transcript_metadata(transcript_id=tct.id)
    if (result["status_code"] < 300):
        if result["title"]:
            tct.title = result["title"]
        if result["interviewees"]:
            tct.interviewee_names = result["interviewees"]
        if result["interviewers"]:
            tct.interviewer_names = result["interviewers"]
        tct.metadata_generated = True
        tct.cost += Decimal(result["cost"])
        tct.save()
    return result


def _update_synthesis_from_result(tct: Transcript,
                                  synthesis: Synthesis,
                                  result: dict) -> None:
    """Create a synthesis object from the result of a synthesis request."""
    if (result['status_code'] < 300):
        synthesis.output = result["output"]
        synthesis.prompt = result["prompt"]
        synthesis.cost = Decimal(result["cost"])
        synthesis.status = SynthesisStatus.COMPLETED
        synthesis.save()

        tct.cost += synthesis.cost
        tct.save()
    else:
        synthesis.status = SynthesisStatus.FAILED
        synthesis.save()


def generate_summary(tct: Transcript) -> dict:
    """Generate synthesized summary using the synthesis service"""
    try:
        synthesis = Synthesis.objects.get(
            transcript=tct,
            output_type=SynthesisType.SUMMARY
        )
        # TODO: add support for multiple interviewees
        result = synthesis_client.get_summary_with_citations(
            transcript_id=tct.id,
            interviewee=tct.interviewee_names[0]
        )
        _update_synthesis_from_result(tct, synthesis, result)
    except Synthesis.DoesNotExist as e:
        logger.exception(("Synthesis doesn't exist. "
                          "Summary generation will be skipped."),
                         exc_info=e)
        result = {'status_code': 500}
    return result


def generate_concise(tct: Transcript) -> dict:
    """Generate concise transcript using the synthesis service"""
    try:
        synthesis = Synthesis.objects.get(
            transcript=tct,
            output_type=SynthesisType.CONCISE
        )
        # TODO: add support for multiple interviewees
        result = synthesis_client.get_concise_with_citations(
            transcript_id=tct.id,
            interviewee=tct.interviewee_names[0]
        )
        _update_synthesis_from_result(tct, synthesis, result)
    except Synthesis.DoesNotExist as e:
        logger.exception(("Synthesis doesn't exist. "
                          "Concise generation will be skipped."),
                         exc_info=e)
        result = {'status_code': 500}
    return result


def generate_embeds(tct: Transcript) -> dict:
    """Generate the embeds for the transcript."""
    try:
        embeds = Embeds.objects.get(
            transcript=tct
        )
        # TODO: add support for multiple interviewees
        result = synthesis_client.generate_embeds(
            transcript_id=tct.id,
            transcript_title=tct.title,
            interviewee=tct.interviewee_names[0]
        )
        if (result['status_code'] < 300):
            embeds.cost = Decimal(result["cost"])
            embeds.status = SynthesisStatus.COMPLETED
            embeds.save()

            tct.cost += embeds.cost
            tct.save()
        else:
            embeds.status = SynthesisStatus.FAILED
            embeds.save()
    except Embeds.DoesNotExist as e:
        logger.exception(("Embeds Object doesn't exist. "
                          "Embeds generation will be skipped."),
                         exc_info=e)
        result = {'status_code': 500}
    return result


def generate_answers(tct: Transcript) -> 'list[dict]':
    questions = tct.project.questions
    query_objects = []
    for question in questions:
        query_obj = run_openai_query(
            tct, question,
            Query.QueryLevelChoices.PROJECT)
        data = {
                'query': question,
                'output': query_obj.output
            }
        query_objects.append(data)
    return query_objects


def run_openai_query(tct: Transcript, query: str, level: str) -> Query:
    """Run the OpenAI query on the given transcript."""
    result = synthesis_client.run_query(tct.id, query)
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

    return query_obj
