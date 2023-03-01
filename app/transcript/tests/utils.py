"""
Utility functions for testing the transcript app.
"""
from django.contrib.auth import get_user_model

from transcript.models import Transcript, AISynthesis


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


def create_transcript(user, **params):
    """Create and return a sample transcript."""
    defaults = {
        'title': 'Test Title',
        'interviewee_names': ['Interviewee'],
        'interviewer_names': ['Interviewer 1', 'Interviewer 2'],
        'transcript': 'Test Transcript',
    }
    defaults.update(params)

    tpt = Transcript.objects.create(user=user, **defaults)
    tpt.summary = AISynthesis.objects.create(
        output_type=AISynthesis.SynthesisType.SUMMARY,
        output='Test Summary'
    )
    tpt.save()
    return tpt
