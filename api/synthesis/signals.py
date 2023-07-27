from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ProcessedTranscript
from .server import embeds_client


@receiver(post_delete, sender=ProcessedTranscript)
def delete_embeddings(sender, instance, **kwargs):
    return _delete_embeddings(sender, instance, **kwargs)


# Necessary to create helper for mocking in tests
def _delete_embeddings(sender, instance, **kwargs):
    """Generate Embeddings from the Embeds Client"""
    embeds_client.delete(instance.id)
