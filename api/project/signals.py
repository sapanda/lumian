from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from . import samples
from .models import Project


User = get_user_model()


@receiver(post_save, sender=User)
def create_sample_project(sender, instance, **kwargs):
    _create_sample_project(sender, instance, **kwargs)


# Necessary to create helper for mocking in tests
def _create_sample_project(sender, instance, **kwargs):
    """Create sample project with sample content"""
    samples.create_project(instance)


@receiver(post_delete, sender=User)
def delete_projects_for_user(sender, instance, **kwargs):
    _delete_projects_for_user(sender, instance, **kwargs)


# Necessary to create helper for mocking in tests
def _delete_projects_for_user(sender, instance, **kwargs):
    """Delete all projects for a user"""
    Project.objects.filter(user=instance).delete()
