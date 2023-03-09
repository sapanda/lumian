from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from transcript.models import Transcript, AIChunks, AISynthesis
from transcript.tasks import generate_summary


@receiver(post_save, sender=Transcript)
def run_generate_synthesis(sender, instance, created, **kwargs):
    return _run_generate_synthesis(sender, instance, created, **kwargs)


# Necessary to create helper for mocking in tests
def _run_generate_synthesis(sender, instance, created, **kwargs):
    """Generate AI Synthesis for the transcript object"""
    if created:
        generate_summary.delay(instance.id)


@receiver(post_delete, sender=Transcript)
def auto_delete_synthesis_with_transcript(sender, instance, **kwargs):
    return _auto_delete_synthesis_with_transcript(
        sender, instance, **kwargs)


# Necessary to create helper for mocking in tests
def _auto_delete_synthesis_with_transcript(sender, instance, **kwargs):
    """Delete AI synthesis when transcript is deleted"""
    AIChunks.objects.filter(transcript=instance).delete()
    AISynthesis.objects.filter(transcript=instance).delete()
