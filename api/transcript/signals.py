from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from .models import Transcript
from app import settings
from core.gcloud_client import client


@receiver(post_save, sender=Transcript)
def run_generate_synthesis(sender, instance, created, **kwargs):
    return _run_generate_synthesis(sender, instance, created, **kwargs)


# Necessary to create helper for mocking in tests
def _run_generate_synthesis(sender, instance, created, **kwargs):
    """Generate AI Synthesis for the transcript object"""
    if created and not settings.TESTING:  # HACK to prevent trigger in tests
        client.create_task(
            path=reverse('transcript:initiate-synthesis',
                         args=[instance.id]),
            payload=''
        )
