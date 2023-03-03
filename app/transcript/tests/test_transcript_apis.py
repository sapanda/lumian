"""
Tests for the creation and upload of transcripts via the API.
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from transcript.models import Transcript
from transcript.serializers import TranscriptSerializer
from transcript.tests.utils import create_user, create_transcript

from unittest.mock import patch


TRANSCRIPT_URL = reverse('transcript:transcript-list')


def detail_url(transcript_id):
    """Create and return a transcript detail URL."""
    return reverse('transcript:transcript-detail', args=[transcript_id])


def summary_url(transcript_id):
    """Create and return a summary detail URL."""
    return reverse('transcript:summary-detail', args=[transcript_id])


class PublicTranscriptAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(TRANSCRIPT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTranscriptAPITests(TestCase):
    """Test the transcript creation features"""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch('transcript.signals._run_generate_synthesis')
    def test_create_transcript_success(self, patched_signal):
        """Test creating a transcript is successful."""
        payload = {
            'title': 'Test Title',
            'interviewee_names': ['Interviewee'],
            'interviewer_names': ['Interviewer 1', 'Interviewer 2'],
            'transcript': 'Test Transcript',
        }
        res = self.client.post(TRANSCRIPT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tpt = Transcript.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(tpt, k), v)
        self.assertEqual(tpt.user, self.user)
        self.assertEqual(patched_signal.call_count, 1)

    @patch('transcript.signals._run_generate_synthesis')
    def test_create_blank_input_failure(self, patched_signal):
        """Test creating a transcript with blank input fails."""
        payload = {
            'title': '',
            'interviewee_names': [''],
            'interviewer_names': [''],
            'transcript': '',
        }
        res = self.client.post(TRANSCRIPT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['title'][0],
                         'This field may not be blank.')
        self.assertEqual(res.data['interviewee_names'][0][0],
                         'This field may not be blank.')
        self.assertEqual(res.data['interviewer_names'][0][0],
                         'This field may not be blank.')
        self.assertEqual(patched_signal.call_count, 0)

    def test_retrieve_transcripts(self):
        """Test retrieving a list of transcripts."""
        create_transcript(user=self.user)
        create_transcript(user=self.user)

        res = self.client.get(TRANSCRIPT_URL)

        trancripts = Transcript.objects.all().order_by('-id')
        serializer = TranscriptSerializer(trancripts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_transcript_list_limited_to_user(self):
        """Test list of transcripts is limited to authenticated user."""
        other_user = create_user(email='other@example.com', password='test123')
        create_transcript(user=other_user)
        create_transcript(user=self.user)

        res = self.client.get(TRANSCRIPT_URL)

        transcripts = Transcript.objects.filter(user=self.user)
        serializer = TranscriptSerializer(transcripts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update(self):
        """Test partial update of a transcript."""
        tpt = create_transcript(user=self.user)

        payload = {'title': 'New Title', 'interviewee_names': ['New Guy']}
        url = detail_url(tpt.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tpt.refresh_from_db()
        self.assertEqual(tpt.title, payload['title'])
        self.assertEqual(tpt.interviewee_names, payload['interviewee_names'])
        self.assertEqual(tpt.user, self.user)

    def test_full_update(self):
        """Test full update of transcript."""
        tpt = create_transcript(user=self.user)

        payload = {
            'title': 'New Title',
            'interviewee_names': ['New Guy'],
            'interviewer_names': ['New Interviewer 1', 'New Interviewer 2'],
            'transcript': 'New Transcript',
        }
        url = detail_url(tpt.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tpt.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(tpt, k), v)
        self.assertEqual(tpt.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the transcript user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        tpt = create_transcript(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(tpt.id)
        self.client.patch(url, payload)

        tpt.refresh_from_db()
        self.assertEqual(tpt.user, self.user)

    def test_delete_transcript(self):
        """Test deleting a transcript successful."""
        tpt = create_transcript(user=self.user)

        url = detail_url(tpt.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Transcript.objects.filter(id=tpt.id).exists())

    def test_transcript_other_users_transcript_error(self):
        """Test trying to delete another users transcript gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        tpt = create_transcript(user=new_user)

        url = detail_url(tpt.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Transcript.objects.filter(id=tpt.id).exists())

    def test_summary_in_progress(self):
        """Test getting a summary of a transcript that is in progress."""
        tpt = Transcript.objects.create(
            user=self.user,
            title='Test Title',
            interviewee_names=['Test Interviewee'],
            interviewer_names=['Test Interviewer'],
            transcript='Test Transcript',
        )

        url = summary_url(tpt.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNone(res.data)

    def test_summary_valid(self):
        """Test getting a summary of a transcript."""
        tpt = create_transcript(user=self.user)

        url = summary_url(tpt.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['output'], tpt.summary.output)

    def test_summary_invalid_transcript(self):
        """Test getting a summary of a transcript that does not exist."""
        url = summary_url(10000000)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
