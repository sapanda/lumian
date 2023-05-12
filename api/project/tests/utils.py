"""
Utility functions for testing the project app.
"""
from django.contrib.auth import get_user_model

from project.models import Project


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


def create_project(user, **params):
    """Create and return a project."""
    defaults = {
        'title': 'Test Project',
        'questions': ['What is a cow?', 'Why do birds fly?'],
    }
    defaults.update(params)

    pjt = Project.objects.create(user=user, **defaults)
    pjt.save()
    return pjt
