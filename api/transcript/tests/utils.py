"""
Utility functions for testing the transcript app.
"""
from django.contrib.auth import get_user_model

from project.models import Project
from transcript.models import (
    Transcript, SynthesisType, Synthesis, Embeds
)


TEST_INDEX_NAME = 'synthesis-api-test'


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


def default_transcript_payload(project):
    """Return a default transcript payload."""
    return {
        'project': project.id,
        'title': 'Test Title',
        'interviewee_names': ['Interviewee'],
        'interviewer_names': ['Interviewer 1', 'Interviewer 2'],
        'transcript': 'Test Transcript',
    }


def create_transcript(project, **params):
    """Create and return a sample transcript."""
    defaults = {
        'title': 'Test Title',
        'interviewee_names': ['Interviewee'],
        'interviewer_names': ['Interviewer 1', 'Interviewer 2'],
        'transcript': 'Test Transcript',
    }
    defaults.update(params)

    tct = Transcript.objects.create(project=project, **defaults)
    tct.save()

    Synthesis.objects.create(
        transcript=tct,
        output_type=SynthesisType.SUMMARY,
        output=[{'text': 'summary'}],
        cost=0.1,
    )
    Synthesis.objects.create(
        transcript=tct,
        output_type=SynthesisType.CONCISE,
        output=[{'text': 'concise'}],
        cost=0.2,
    )
    Embeds.objects.create(
        transcript=tct,
        cost=0.05,
    )
    return tct
