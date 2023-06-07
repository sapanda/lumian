from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse

from .models import Transcript
from .synthesis_client import delete_transcript_for_id
from core.gcloud_client import client


@receiver(post_save, sender=Transcript)
def run_generate_synthesis(sender, instance, created, **kwargs):
    return _run_generate_synthesis(sender, instance, created, **kwargs)


# Necessary to create helper for mocking in tests
def _run_generate_synthesis(sender, instance, created, **kwargs):
    """Generate AI Synthesis for the transcript object"""
    if created:
        client.create_task(
            path=reverse('transcript:initiate-synthesis',
                         args=[instance.id]),
            payload=''
        )


@receiver(post_delete, sender=Transcript)
def delete_transcript_on_synthesis_service(sender, instance, **kwargs):
    _delete_transcript_on_synthesis_service(sender, instance, **kwargs)


# Necessary to create helper for mocking in tests
def _delete_transcript_on_synthesis_service(sender, instance, **kwargs):
    """Delete transcript from Synthesis Service"""
    delete_transcript_for_id(instance.id)
