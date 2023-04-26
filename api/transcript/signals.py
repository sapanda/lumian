from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from transcript.models import Transcript
from transcript.tasks import generate_synthesis
from transcript.synthesis_core import delete_transcript_for_id


@receiver(post_save, sender=Transcript)
def run_generate_synthesis(sender, instance, created, **kwargs):
    return _run_generate_synthesis(sender, instance, created, **kwargs)


# Necessary to create helper for mocking in tests
def _run_generate_synthesis(sender, instance, created, **kwargs):
    """Generate AI Synthesis for the transcript object"""
    if created:
        generate_synthesis.delay(instance.id)


@receiver(post_delete, sender=Transcript)
def delete_transcript_on_synthesis_service(sender, instance, **kwargs):
    _delete_transcript_on_synthesis_service(sender, instance, **kwargs)


# Necessary to create helper for mocking in tests
def _delete_transcript_on_synthesis_service(sender, instance, **kwargs):
    """Delete transcript from Synthesis Service"""
    delete_transcript_for_id(instance.id)
