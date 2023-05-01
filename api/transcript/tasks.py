from transcript import synthesis_client
from transcript.models import (
    Transcript, SynthesisType, Query,
    Embeds, Synthesis
)


def _generate_summary(tct: Transcript) -> Synthesis:
    """Generate synthesized summary using the synthesis service"""
    # TODO: add support for multiple interviewees
    response = synthesis_client.get_summary_with_citations(
        transcript_id=tct.id,
        interviewee=tct.interviewee_names[0]
    )
    if (response.status_code < 300):
        result = response.json()
        return Synthesis.objects.create(
            transcript=tct,
            output_type=SynthesisType.SUMMARY,
            output=result["output"],
            prompt=result["prompt"],
            cost=result["cost"]
        )


def _generate_concise(tct: Transcript) -> Synthesis:
    """Generate concise transcript using the synthesis service"""
    # TODO: add support for multiple interviewees
    response = synthesis_client.get_concise_with_citations(
        transcript_id=tct.id,
        interviewee=tct.interviewee_names[0]
    )
    if (response.status_code < 300):
        result = response.json()
        return Synthesis.objects.create(
            transcript=tct,
            output_type=SynthesisType.CONCISE,
            output=result["output"],
            prompt=result["prompt"],
            cost=result["cost"]
        )


def _generate_embeds(tct: Transcript) -> Embeds:
    """Generate the embeds for the transcript."""
    response = synthesis_client.generate_embeds(
        transcript_id=tct.id,
        transcript_title=tct.title,
        interviewee=tct.interviewee_names[0]
    )
    if (response.status_code < 300):
        result = response.json()
        return Embeds.objects.create(
            transcript=tct,
            cost=result["cost"]
        )


def generate_synthesis(transcript_id) -> int:
    """Generate synthesized outputs using the synthesis service"""
    tct = Transcript.objects.get(id=transcript_id)
    synthesis_client.save_transcript_for_id(
        transcript_id=tct.id, transcript=tct.transcript
    )
    summary = _generate_summary(tct)
    concise = _generate_concise(tct)
    embeds = _generate_embeds(tct)

    if summary and concise and embeds:
        tct.cost = summary.cost + concise.cost + embeds.cost
        tct.save()
        return 200

    return 500


def run_openai_query(tct: Transcript, query: str) -> Query:
    """Run the OpenAI query on the given transcript."""
    response = synthesis_client.run_query(tct.id, query)
    result = response.json()
    query_obj = Query.objects.create(
        transcript=tct,
        query=query,
        output=result['output'],
        prompt=result["prompt"],
        cost=result['cost'],
    )

    tct.cost = float(tct.cost) + query_obj.cost
    tct.save()

    return query_obj
