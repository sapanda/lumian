"""
Tests for the creation and upload of transcripts via the API.
"""
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest import skip
from unittest.mock import patch

from transcript.models import (
    Transcript, SynthesisType, SynthesisStatus, Synthesis, Embeds
)
from transcript.serializers import TranscriptSerializer
from transcript.tasks import generate_embeds
from transcript.tests.utils import (
    create_user,
    create_project,
    create_transcript,
    default_transcript_payload,
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


def synthesis_url(transcript_id):
    """Create and return a generate-synthesis posting URL."""
    return reverse('transcript:generate-synthesis', args=[transcript_id])


class PublicAPITests(APITestCase):
    """Test unauthenticated API requests."""

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(TRANSCRIPT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


@patch('transcript.signals._run_generate_synthesis')
class TranscriptAPITests(APITestCase):
    """Test the API with mocked synthesis service."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client.force_authenticate(user=self.user)
        self.project = create_project(user=self.user)

    def set_superuser(self, is_superuser: bool):
        """Set the user to be a superuser."""
        self.user.is_superuser = is_superuser
        self.user.save()

    def test_create_transcript_success(self, patched_signal):
        """Test creating a transcript is successful."""
        payload = default_transcript_payload(self.project)
        res = self.client.post(TRANSCRIPT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tpt = Transcript.objects.get(id=res.data['data']['id'])
        for k, v in payload.items():
            if k != 'file':
                attr = getattr(tpt, k)
                if not isinstance(attr, Project):
                    self.assertEqual(attr, v)
        self.assertEqual(patched_signal.call_count, 1)

    def test_create_transcript_failure(self, patched_signal):
        """Test creating a transcript with blank input fails."""
        file = open('transcript/tests/data/sample_transcript.txt',
                    'r', encoding='utf-8')
        payload = {
            'project': self.project.id,
            'title': '',
            'interviewee_names': [''],
            'interviewer_names': [''],
            'file': file,
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
        file.close()

    def test_create_transcript_alt_user(self, patched_signal):
        """Test creating a transcript with a different user fails
        for both regular and super users."""
        new_user = create_user(email='user2@example.com', password='test123')
        new_project = create_project(user=new_user)
        file = open('transcript/tests/data/sample_transcript.txt',
                    'r', encoding='utf-8')
        payload = {
            'project': new_project.id,
            'title': 'Test Title',
            'interviewee_names': ['Interviewee'],
            'interviewer_names': ['Interviewer 1', 'Interviewer 2'],
            'file': file,
        }
        res = self.client.post(TRANSCRIPT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.set_superuser(True)
        file.seek(0)
        res = self.client.post(TRANSCRIPT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_transcripts(self, patched_signal):
        """Test retrieving a list of transcripts."""
        create_transcript(project=self.project)
        create_transcript(project=self.project)

        res = self.client.get(TRANSCRIPT_URL)

        trancripts = Transcript.objects.all().order_by('-id')
        serializer = TranscriptSerializer(trancripts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['data']['transcripts'], serializer.data)

    def test_retrieve_transcript_alt_user(self, patched_signal):
        """Test retrieving a single transcript should fail
        with wrong user unless superuser."""
        other_user = create_user(email='other@example.com', password='test123')
        other_project = create_project(user=other_user)
        tct = create_transcript(project=other_project)

        url = detail_url(tct.id)

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.set_superuser(True)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_transcript_list_limited_to_user(self, patched_signal):
        """Test list of transcripts is limited to authenticated user
        unless requestor is a superuser."""
        other_user = create_user(email='other@example.com', password='test123')
        other_project = create_project(user=other_user)
        create_transcript(project=other_project)
        create_transcript(project=self.project)

        res = self.client.get(TRANSCRIPT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 3)
        expected_transcripts = 2  # 1 + 1x Sample Transcript
        self.assertEqual(len(res.data['data']['transcripts']),
                         expected_transcripts)
        self.assertEqual(res.data['data']['transcripts'][0]['project'],
                         self.project.id)

        self.set_superuser(True)
        res = self.client.get(TRANSCRIPT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        expected_transcripts = 5  # 2 + 3x Sample Transcripts
        self.assertEqual(len(res.data['data']['transcripts']),
                         expected_transcripts)

    def test_transcript_filter(self, patched_signal):
        """Test filtering the transcript list to requested project."""
        my_new_project = create_project(user=self.user)
        create_transcript(project=self.project)
        create_transcript(project=my_new_project)

        payload = {'project': self.project.id}
        res = self.client.get(TRANSCRIPT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 3)
        self.assertEqual(len(res.data['data']['transcripts']), 1)
        self.assertEqual(res.data['data']['transcripts'][0]['project'],
                         self.project.id)

    def test_transcript_filter_alt_user(self, patched_signal):
        """Test filtering the transcript list to requested project
        for a superuser."""
        other_user = create_user(email='other@example.com', password='test123')
        other_project = create_project(user=other_user)
        create_transcript(project=other_project)
        create_transcript(project=self.project)

        self.set_superuser(True)

        payload = {'project': self.project.id}
        res = self.client.get(TRANSCRIPT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 3)
        self.assertEqual(len(res.data['data']['transcripts']), 1)
        self.assertEqual(res.data['data']['transcripts'][0]['project'],
                         self.project.id)

        res = self.client.get(TRANSCRIPT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 3)
        expected_transcripts = 5  # 2 + 3x Sample Transcripts
        self.assertEqual(len(res.data['data']['transcripts']),
                         expected_transcripts)

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

    def test_partial_update_alt_user(self, patched_signal):
        """Test partial update of a transcript in another user's project fails
        for both regular and super users."""
        other_user = create_user(email='other@example.com', password='test123')
        other_project = create_project(user=other_user)
        tpt = create_transcript(project=other_project)
        payload = {'title': 'New Title', 'interviewee_names': ['New Guy']}

        url = detail_url(tpt.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.set_superuser(True)
        url = detail_url(tpt.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_transcript(self, patched_signal):
        """Test deleting a transcript successful."""
        tpt = create_transcript(project=self.project)
        url = detail_url(tpt.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(Transcript.objects.filter(id=tpt.id).exists())

    def test_delete_transcript_alt_user(self, patched_signal):
        """Test trying to delete another users transcript gives error
        for both regular and super users."""
        new_user = create_user(email='user2@example.com', password='test123')
        new_project = create_project(user=new_user)
        tpt = create_transcript(project=new_project)

        url = detail_url(tpt.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Transcript.objects.filter(id=tpt.id).exists())

        self.set_superuser(True)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_summary_in_progress(self, patched_signal):
        """Test getting a summary of a transcript that is in progress."""
        payload = default_transcript_payload(self.project)
        res = self.client.post(TRANSCRIPT_URL, payload)

        url = summary_url(res.data['data']['id'])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNone(res.data)

    def test_summary_valid(self, patched_signal):
        """Test getting a summary of a transcript."""
        payload = default_transcript_payload(self.project)
        res = self.client.post(TRANSCRIPT_URL, payload)
        tpt = Transcript.objects.get(id=res.data['data']['id'])
        summary = Synthesis.objects.get(
            transcript=tpt,
            output_type=SynthesisType.SUMMARY
        )
        summary.status = SynthesisStatus.COMPLETED
        summary.save()

        url = summary_url(tpt.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['output'], summary.output)

    def test_summary_invalid_transcript(self, patched_signal):
        """Test getting a summary of a transcript that does not exist."""
        url = summary_url(10000000)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_summary_alt_user(self, patched_signal):
        """Test getting a summary of a transcript fails for the wrong user
        if requestor is regular user or but succeeds for superuser."""
        other_user = create_user(email='other@example.com', password='test123')
        other_project = create_project(user=other_user)
        tpt = create_transcript(project=other_project)
        summary = Synthesis.objects.get(
            transcript=tpt,
            output_type=SynthesisType.SUMMARY
        )
        summary.status = SynthesisStatus.COMPLETED
        summary.save()

        url = summary_url(tpt.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.set_superuser(True)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_concise_in_progress(self, patched_signal):
        """Test getting a concise transcript that is in progress."""
        payload = default_transcript_payload(self.project)
        res = self.client.post(TRANSCRIPT_URL, payload)

        url = concise_url(res.data['data']['id'])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertIsNone(res.data)

    def test_concise_valid(self, patched_signal):
        """Test getting a concise transcript."""
        payload = default_transcript_payload(self.project)
        res = self.client.post(TRANSCRIPT_URL, payload)
        tpt = Transcript.objects.get(id=res.data['data']['id'])
        concise = Synthesis.objects.get(
            transcript=tpt,
            output_type=SynthesisType.CONCISE
        )
        concise.status = SynthesisStatus.COMPLETED
        concise.save()

        url = concise_url(tpt.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['output'], concise.output)

    def test_concise_invalid_transcript(self, patched_signal):
        """
        Test getting a concise transcript of a transcript that does not exist.
        """
        url = concise_url(10000000)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_concise_alt_user(self, patched_signal):
        """Test getting a concise of a transcript fails for the wrong user
        if requestor is regular user or but succeeds for superuser."""
        other_user = create_user(email='other@example.com', password='test123')
        other_project = create_project(user=other_user)
        tpt = create_transcript(project=other_project)
        concise = Synthesis.objects.get(
            transcript=tpt,
            output_type=SynthesisType.CONCISE
        )
        concise.status = SynthesisStatus.COMPLETED
        concise.save()

        url = concise_url(tpt.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.set_superuser(True)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @patch('synthesis.usecases.run_transcript_query')
    def test_query_success(self, patched_query, patched_signal):
        """Test querying a transcript successfully."""
        tpt = create_transcript(project=self.project)
        embeds = Embeds.objects.get(transcript=tpt)
        embeds.status = SynthesisStatus.COMPLETED
        embeds.save()

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

    @patch('synthesis.usecases.run_transcript_query')
    def test_query_list_empty(self, patched_query, patched_signal):
        """Test that the query GET request works with empty results."""
        tpt = create_transcript(project=self.project)
        url = query_url(tpt.id)
        url = f"{url}?query_level=transcript"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)

    def test_query_list_invalid_transcript(self, patched_signal):
        """Test that the query GET request fails with invalid transcript."""
        url = query_url(10000000)
        url = f"{url}?query_level=transcript"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    @patch('synthesis.usecases.run_transcript_query')
    def test_query_alt_user(self, patched_query, patched_signal):
        """Test that query fails when user is not the owner of the project
        regardless of whether the user is a superuser."""
        other_user = create_user(email='other@example.com', password='test123')
        other_project = create_project(user=other_user)
        tpt = create_transcript(project=other_project)
        embeds = Embeds.objects.get(transcript=tpt)
        embeds.status = SynthesisStatus.COMPLETED
        embeds.save()

        query = "empty?"
        query_output = {'output': 'empty', 'prompt': 'empty', 'cost': 0.3, }
        patched_query.return_value = query_output

        url = query_url(tpt.id)
        res = self.client.post(url, {'query': query})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.set_superuser(True)
        res = self.client.post(url, {'query': query})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    @patch('synthesis.usecases.run_transcript_query')
    def test_query_list_alt_user(
            self, patched_query, patched_signal):
        """Test that query list fails when user is not the owner
        of the project, unless the user is a superuser."""
        other_user = create_user(email='other@example.com', password='test123')
        other_project = create_project(user=other_user)
        tpt = create_transcript(project=other_project)
        url = query_url(tpt.id)
        url = f"{url}?query_level=transcript"

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.set_superuser(True)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)


@skip("OpenAI Costs: Run only when testing AI Synthesis changes")
@patch('transcript.signals._run_generate_synthesis')
class EndToEndQueryTests(APITestCase):
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
        generate_embeds(self.tct)
        query = "Where does Jason live?"
        url = query_url(self.tct.id)
        res = self.client.post(url, {'query': query})

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['data']['query'],
                         query,
                         "Wrong query string")
        self.assertTrue('Boise' in res.data['data']['result'], "Bad result")

    @skip("Needs synthesis Service to be running")
    def test_query_list_valid(self, patched_signal):
        """Test that the query GET request is successfully executed."""
        generate_embeds(self.tct)
        url = query_url(self.tct.id)
        self.client.post(url, {'query': 'Where does Jason live?'})
        self.client.post(url, {'query': 'Describe Jason\'s family?'})

        url = f"{url}?query_level=transcript"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 2)
