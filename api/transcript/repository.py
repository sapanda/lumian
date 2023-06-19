from transcript.models import (
    Transcript, Synthesis, Embeds, SynthesisType
)


def create_synthesis_entry(tct: Transcript):
    Synthesis.objects.create(
        transcript=tct,
        output_type=SynthesisType.SUMMARY
    )
    Synthesis.objects.create(
        transcript=tct,
        output_type=SynthesisType.CONCISE
    )
    Embeds.objects.create(transcript=tct)
