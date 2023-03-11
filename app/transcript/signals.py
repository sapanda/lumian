from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from pinecone import delete_index

from transcript.models import Transcript, AIEmbeds
from transcript.tasks import generate_synthesis


@receiver(post_save, sender=Transcript)
def run_generate_synthesis(sender, instance, created, **kwargs):
    return _run_generate_synthesis(sender, instance, created, **kwargs)


# Necessary to create helper for mocking in tests
def _run_generate_synthesis(sender, instance, created, **kwargs):
    """Generate AI Synthesis for the transcript object"""
    if created:
        generate_synthesis.delay(instance.id)


@receiver(post_delete, sender=AIEmbeds)
def auto_delete_pinecone_index(sender, instance, **kwargs):
    delete_index(instance.index_name)
