"""
Utility functions for testing the transcript app.
"""
from django.contrib.auth import get_user_model
from transcript.models import Transcript, AISynthesis, SynthesisType


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
    tpt.save()

    summary = AISynthesis.objects.create(
        transcript=tpt,
        output_type=SynthesisType.SUMMARY,
        output='Test Summary',
        tokens_used=100,
    )
    summary.save()

    concise = AISynthesis.objects.create(
        transcript=tpt,
        output_type=SynthesisType.CONCISE,
        output='Test Concise',
        tokens_used=0,
    )
    concise.save()
    return tpt
