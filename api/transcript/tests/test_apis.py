"""
Tests for the creation and upload of transcripts via the API.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest import skip
from unittest.mock import patch

from transcript.models import Transcript, SynthesisType, Synthesis
from transcript.serializers import TranscriptSerializer
from transcript.synthesis_client import generate_embeds
from transcript.tests.utils import (
    create_user,
    create_project,
    create_transcript,
)
from project.models import Project


TRANSCRIPT_URL = reverse('transcript:transcript-list')


def detail_url(transcript_id):
    """Create and return a transcript detail URL."""
    return reverse('transcript:transcript-detail', args=[transcript_id])


def summary_url(transcript_id):
    """Create and return a summary detail URL."""
    return reverse('transcript:summary-detail', args=[transcript_id])


def concise_url(transcript_id):
    """Create and return a concise detail URL."""
    return reverse('transcript:concise-detail', args=[transcript_id])


def query_url(transcript_id):
    """Create and return a query posting URL."""
    return reverse('transcript:query-detail', args=[transcript_id])


class PublicAPITests(APITestCase):
    """Test unauthenticated API requests."""

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(TRANSCRIPT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


@patch('transcript.signals._run_generate_synthesis')
class MockAPITests(APITestCase):
    """Test the API with mocked synthesis service."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client.force_authenticate(user=self.user)
        self.project = create_project(user=self.user)

    def test_create_transcript_success(self, patched_signal):
        """Test creating a transcript is successful."""
        payload = {
            'project': self.project.id,
            'title': 'Test Title',
            'interviewee_names': ['Interviewee'],
            'interviewer_names': ['Interviewer 1', 'Interviewer 2'],
            'transcript': 'Test Transcript',
        }
        res = self.client.post(TRANSCRIPT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tpt = Transcript.objects.get(id=res.data['id'])
        for k, v in payload.items():
            attr = getattr(tpt, k)
            if not isinstance(attr, Project):
                self.assertEqual(attr, v)
        self.assertEqual(patched_signal.call_count, 1)

    def test_create_transcript_failure(self, patched_signal):
        """Test creating a transcript with blank input fails."""
        payload = {
            'project': self.project.id,
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

    def test_retrieve_transcripts(self, patched_signal):
        """Test retrieving a list of transcripts."""
        create_transcript(project=self.project)
        create_transcript(project=self.project)

        res = self.client.get(TRANSCRIPT_URL)

        trancripts = Transcript.objects.all().order_by('-id')
        serializer = TranscriptSerializer(trancripts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_transcript_list_limited_to_user(self, patched_signal):
        """Test list of transcripts is limited to authenticated user."""
        other_user = create_user(email='other@example.com', password='test123')
        other_project = create_project(user=other_user)
        create_transcript(project=other_project)
        create_transcript(project=self.project)

        res = self.client.get(TRANSCRIPT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['project'], self.project.id)

    def test_transcript_filter(self, patched_signal):
        """Test filtering the transcript list to requested project."""
        new_project = create_project(user=self.user)
        create_transcript(project=self.project)
        create_transcript(project=new_project)

        payload = {'project': self.project.id}
        res = self.client.get(TRANSCRIPT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['project'], self.project.id)

    def test_partial_update(self, patched_signal):
        """Test partial update of a transcript."""
        tpt = create_transcript(project=self.project)
        old_interviewer_names = tpt.interviewer_names

        payload = {'title': 'New Title', 'interviewee_names': ['New Guy']}
        url = detail_url(tpt.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tpt.refresh_from_db()
        self.assertEqual(tpt.title, payload['title'])
        self.assertEqual(tpt.interviewee_names, payload['interviewee_names'])
        self.assertEqual(tpt.interviewer_names, old_interviewer_names)

    @patch('transcript.signals._delete_transcript_on_synthesis_service')
    def test_delete_transcript(self, patched_signal, patched_delete):
        """Test deleting a transcript successful."""
        tpt = create_transcript(project=self.project)

        url = detail_url(tpt.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Transcript.objects.filter(id=tpt.id).exists())

    def test_create_transcript_other_users_failure(self, patched_signal):
        """
        Test failure when creating transcript using wrong project ID.
        """
        new_user = create_user(email='user2@example.com', password='test123')
        new_project = create_project(user=new_user)
        payload = {
            'project': new_project.id,
            'title': 'Test Title',
            'interviewee_names': ['Interviewee'],
            'interviewer_names': ['Interviewer 1', 'Interviewer 2'],
            'transcript': 'Test Transcript',
        }
        res = self.client.post(TRANSCRIPT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_transcript_other_users_failure(self, patched_signal):
        """Test trying to delete another users transcript gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        new_project = create_project(user=new_user)
        tpt = create_transcript(project=new_project)

        url = detail_url(tpt.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Transcript.objects.filter(id=tpt.id).exists())

    def test_summary_in_progress(self, patched_signal):
        """Test getting a summary of a transcript that is in progress."""
        tpt = Transcript.objects.create(
            project=self.project,
            title='Test Title',
            interviewee_names=['Test Interviewee'],
            interviewer_names=['Test Interviewer'],
            transcript='Test Transcript',
        )

        url = summary_url(tpt.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNone(res.data)

    def test_summary_valid(self, patched_signal):
        """Test getting a summary of a transcript."""
        tpt = create_transcript(project=self.project)

        url = summary_url(tpt.id)
        res = self.client.get(url)

        summary = Synthesis.objects.get(
            transcript=tpt,
            output_type=SynthesisType.SUMMARY
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['output'], summary.output)

    def test_summary_invalid_transcript(self, patched_signal):
        """Test getting a summary of a transcript that does not exist."""
        url = summary_url(10000000)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_concise_in_progress(self, patched_signal):
        """Test getting a concise transcript that is in progress."""
        tpt = Transcript.objects.create(
            project=self.project,
            title='Test Title',
            interviewee_names=['Test Interviewee'],
            interviewer_names=['Test Interviewer'],
            transcript='Test Transcript',
        )

        url = concise_url(tpt.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNone(res.data)

    def test_concise_valid(self, patched_signal):
        """Test getting a concise transcript."""
        tpt = create_transcript(project=self.project)

        url = concise_url(tpt.id)
        res = self.client.get(url)

        concise = Synthesis.objects.get(
            transcript=tpt,
            output_type=SynthesisType.CONCISE
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['output'], concise.output)

    def test_concise_invalid_transcript(self, patched_signal):
        """
        Test getting a concise transcript of a transcript that does not exist.
        """
        url = concise_url(10000000)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    @patch('transcript.synthesis_client.run_query')
    def test_query_success(self, patched_query, patched_signal):
        """Test querying a transcript successfully."""
        tpt = create_transcript(project=self.project)
        query = "Where does Jason live?"
        query_output = {
            'output': 'Jason lives in Boise',
            'prompt': 'Test prompt',
            'cost': 0.3,
        }
        patched_query.return_value = query_output

        url = query_url(tpt.id)
        res = self.client.post(url, {'query': query})

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['query'], query)
        self.assertEqual(res.data['output'], query_output['output'])

    def test_query_failure_invalid_transcript(self, patched_signal):
        """Test that the query request fails if transcript doesn't exist."""
        url = query_url(10000000)
        res = self.client.post(url, {'query': ''})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    @patch('transcript.synthesis_client.run_query')
    def test_query_list_empty(self, patched_query, patched_signal):
        """Test that the query GET request works with empty results."""
        tpt = create_transcript(project=self.project)
        url = query_url(tpt.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_query_list_invalid_transcript(self, patched_signal):
        """Test that the query GET request fails with invalid transcript."""
        url = query_url(10000000)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


@skip("OpenAI Costs: Run only when testing AI Synthesis changes")
@patch('transcript.signals._run_generate_synthesis')
class EndToEndAPITests(APITestCase):
    """Test the full API endpoints."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client.force_authenticate(user=self.user)
        self.project = create_project(user=self.user)

        with open('transcript/tests/data/transcript_short.txt', 'r') as f:
            sample_transcript = f.read()

        self.tct = create_transcript(
            project=self.project,
            transcript=sample_transcript,
            interviewee_names=['Jason'],
        )

    def tearDown(self):
        pass

    @skip("Needs synthesis Service to be running")
    def test_query_execution_success(self, patched_signal):
        """Test that the query request is successfully executed."""
        generate_embeds(
            self.tct.id, self.tct.title, self.tct.interviewee_names[0]
        )
        query = "Where does Jason live?"
        url = query_url(self.tct.id)
        res = self.client.post(url, {'query': query})

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['query'], query, "Wrong query string")
        self.assertTrue('Boise' in res.data['result'], "Bad result")

    @skip("Needs synthesis Service to be running")
    def test_query_list_valid(self, patched_signal):
        """Test that the query GET request is successfully executed."""
        generate_embeds(
            self.tct.id, self.tct.title, self.tct.interviewee_names[0]
        )
        url = query_url(self.tct.id)
        self.client.post(url, {'query': 'Where does Jason live?'})
        self.client.post(url, {'query': 'Describe Jason\'s family?'})

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
