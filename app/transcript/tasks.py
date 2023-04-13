from celery import shared_task

from transcript import synthesis_core
from transcript.models import (
    Transcript, SynthesisType, Query,
    Embeds, Synthesis
)


def _generate_summary(tct: Transcript) -> Synthesis:
    """Generate synthesized summary using the synthesis service"""
    # TODO: add support for multiple interviewees
    result = synthesis_core.get_summary_with_citations(
        transcript_id=tct.id,
        interviewee=tct.interviewee_names[0]
    )
    return Synthesis.objects.create(
        transcript=tct,
        output_type=SynthesisType.SUMMARY,
        output=result["output"],
        cost=result["cost"]
    )


def _generate_concise(tct: Transcript) -> Synthesis:
    """Generate concise transcript using the synthesis service"""
    # TODO: add support for multiple interviewees
    result = synthesis_core.get_concise_with_citations(
        transcript_id=tct.id,
        interviewee=tct.interviewee_names[0]
    )
    return Synthesis.objects.create(
        transcript=tct,
        output_type=SynthesisType.CONCISE,
        output=result["output"],
        cost=result["cost"]
    )


def _generate_embeds(tct: Transcript) -> Embeds:
    """Generate the embeds for the transcript."""
    result = synthesis_core.generate_embeds(
        transcript_id=tct.id,
        transcript_title=tct.title,
        interviewee=tct.interviewee_names[0]
    )
    return Embeds.objects.create(
        transcript=tct,
        cost=result["cost"]
    )


@shared_task
def generate_synthesis(transcript_id):
    """Generate synthesized outputs using the synthesis service"""
    tct = Transcript.objects.get(id=transcript_id)
    synthesis_core.save_transcript_for_id(
        transcript_id=tct.id, transcript=tct.transcript
    )
    summary = _generate_summary(tct)
    concise = _generate_concise(tct)
    embeds = _generate_embeds(tct)

    tct.cost = summary.cost + concise.cost + embeds.cost
    tct.save()


# TODO: Move to different file?
def run_openai_query(tct: Transcript, query: str) -> Query:
    """Run the OpenAI query on the given transcript."""
    results = synthesis_core.run_query(tct.id, query)
    query_obj = Query.objects.create(
        transcript=tct,
        query=query,
        output=results['output'],
        cost=results['cost'],
    )

    tct.cost = float(tct.cost) + query_obj.cost
    tct.save()

    return query_obj
