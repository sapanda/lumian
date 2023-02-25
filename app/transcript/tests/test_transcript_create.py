"""
Tests for the creation and upload of transcripts via the API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_TRANSCRIPT_URL = reverse('transcript:create')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


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

    def test_create_transcript_success(self):
        """Test creating a transcript is successful."""
        payload = {
            'title': 'Test Title',
            'interviewee_names': ['Interviewee'],
            'interviewer_names': ['Interviewer 1', 'Interviewer 2'],
            'transcript': 'Test Transcript',
        }
        res = self.client.post(CREATE_TRANSCRIPT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['interviewee_names'], payload['interviewee_names'])
        self.assertEqual(res.data['interviewer_names'], payload['interviewer_names'])
        self.assertEqual(res.data['transcript'], payload['transcript'])
