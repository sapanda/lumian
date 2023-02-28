"""
Tests for the creation and upload of transcripts via the API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from transcript.models import Transcript

from unittest.mock import patch


CREATE_TRANSCRIPT_URL = reverse('transcript:create')


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

    transcript = Transcript.objects.create(user=user, **defaults)
    return transcript


@patch('transcript.signals.run_generate_synthesis_helper')
class TranscriptCreateTests(TestCase):
    """Test the transcript creation features"""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_transcript_success(self, patched_signal):
        """Test creating a transcript is successful."""
        payload = {
            'title': 'Test Title',
            'interviewee_names': ['Interviewee'],
            'interviewer_names': ['Interviewer 1', 'Interviewer 2'],
            'transcript': 'Test Transcript',
        }
        res = self.client.post(CREATE_TRANSCRIPT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        transcript = Transcript.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(transcript, k), v)
        self.assertEqual(transcript.user, self.user)
        self.assertEqual(patched_signal.call_count, 1)

    def test_create_blank_input_failure(self, patched_signal):
        """Test creating a transcript with blank input fails."""
        payload = {
            'title': '',
            'interviewee_names': [''],
            'interviewer_names': [''],
            'transcript': '',
        }
        res = self.client.post(CREATE_TRANSCRIPT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['title'][0],
                         'This field may not be blank.')
        self.assertEqual(res.data['interviewee_names'][0][0],
                         'This field may not be blank.')
        self.assertEqual(res.data['interviewer_names'][0][0],
                         'This field may not be blank.')
        self.assertEqual(patched_signal.call_count, 0)
