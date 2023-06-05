from decimal import Decimal
from . import synthesis_client
from .models import Transcript, SynthesisType, Query, Embeds, Synthesis


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


def _create_synthesis_from_result(tct: Transcript,
                                  result: dict,
                                  synthesis_type: SynthesisType) -> Synthesis:
    """Create a synthesis object from the result of a synthesis request."""
    if (result['status_code'] < 300):
        synthesis_obj = Synthesis.objects.create(
            transcript=tct,
            output_type=synthesis_type,
            output=result["output"],
            prompt=result["prompt"],
            cost=Decimal(result["cost"])
        )
        tct.cost += synthesis_obj.cost
        tct.save()
    return synthesis_obj


def generate_summary(tct: Transcript) -> dict:
    """Generate synthesized summary using the synthesis service"""
    # TODO: add support for multiple interviewees
    result = synthesis_client.get_summary_with_citations(
        transcript_id=tct.id,
        interviewee=tct.interviewee_names[0]
    )
    _create_synthesis_from_result(tct, result, SynthesisType.SUMMARY)
    return result


def generate_concise(tct: Transcript) -> dict:
    """Generate concise transcript using the synthesis service"""
    # TODO: add support for multiple interviewees
    result = synthesis_client.get_concise_with_citations(
        transcript_id=tct.id,
        interviewee=tct.interviewee_names[0]
    )
    _create_synthesis_from_result(tct, result, SynthesisType.CONCISE)
    return result


def generate_embeds(tct: Transcript) -> dict:
    """Generate the embeds for the transcript."""
    result = synthesis_client.generate_embeds(
        transcript_id=tct.id,
        transcript_title=tct.title,
        interviewee=tct.interviewee_names[0]
    )
    if (result['status_code'] < 300):
        embeds = Embeds.objects.create(
            transcript=tct,
            cost=Decimal(result["cost"])
        )
        tct.cost += embeds.cost
        tct.save()
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
        level=level
    )

    tct.cost += query_obj.cost
    tct.save()

    return query_obj
