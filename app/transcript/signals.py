from celery import shared_task
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from transcript.models import Transcript, AISynthesis
from transcript.tasks import generate_summary


@shared_task
def populate_summary(obj_id):
    """Populate the summary field of a transcript."""
    tct = Transcript.objects.get(id=obj_id)
    summary = generate_summary(tct.transcript)
    tct.summary = AISynthesis.objects.create(
        output_type=AISynthesis.SynthesisType.SUMMARY,
        output=summary,
    )
    tct.save()


@receiver(post_save, sender=Transcript)
def run_generate_synthesis(sender, instance, created, **kwargs):
    """Necessary to create helper for mocking in tests"""
    return run_generate_synthesis_helper(sender, instance, created, **kwargs)


def run_generate_synthesis_helper(sender, instance, created, **kwargs):
    """Generate AI Synthesis for the transcript object"""
    if created:
        populate_summary.delay(instance.id)


@receiver(post_delete, sender=Transcript)
def auto_delete_summary_with_transcript(sender, instance, **kwargs):
    """Necessary to create helper for mocking in tests"""
    return auto_delete_summary_with_transcript_helper(sender, instance, **kwargs)


def auto_delete_summary_with_transcript_helper(sender, instance, **kwargs):
    """Delete summary when transcript is deleted"""
    instance.summary.delete()
