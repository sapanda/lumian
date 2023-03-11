"""
Utility functions for testing the transcript app.
"""
from django.contrib.auth import get_user_model

from transcript.models import (
    Transcript, AISynthesis, SynthesisType, AIEmbeds
)
from transcript.tasks import (
    OPENAI_EMBEDDING_DIMENSIONS,
    _generate_chunks,
    _execute_openai_embeds_and_upsert,
    _init_pinecone_index,
)

from pinecone import list_indexes


TEST_INDEX_NAME = 'synthesis-api-test'


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


def create_embeds(tct: Transcript):
    embeds = AIEmbeds.objects.create(
        transcript=tct,
        chunks=[],
        index_name=TEST_INDEX_NAME
    )
    embeds.save()
    return embeds


def create_pinecone_index(tct: Transcript):
    """Create and populate the index if it doesn't exist."""
    if TEST_INDEX_NAME not in list_indexes():
        index = _init_pinecone_index(index_name=TEST_INDEX_NAME,
                                     dimension=OPENAI_EMBEDDING_DIMENSIONS)
        chunks = _generate_chunks(tct)
        _execute_openai_embeds_and_upsert(index, chunks)
