"""
Tests for project management via the API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from project.models import Project
from project.samples import load_content
from transcript.models import Transcript


class UserManagementTests(TestCase):
    """Test sample content creation."""

    def setUp(self):
        self.sample_content = load_content()

    def test_create_user_sample_success(self):
        """Test creating a new user successfully creates a sample project."""
        user = get_user_model().objects.create_user("a@b.com", 'sample123')

        pjt = Project.objects.get(user=user)
        self.assertEqual(pjt.title, self.sample_content['project']['title'])
        self.assertEqual(pjt.goal, self.sample_content['project']['goal'])
        self.assertEqual(
            pjt.questions, self.sample_content['project']['questions'])

        tct = Transcript.objects.get(project=pjt)
        self.assertEqual(
            tct.title,
            self.sample_content['transcript']['title'])
        self.assertEqual(
            tct.interviewee_names,
            self.sample_content['transcript']['interviewee_names'])
        self.assertEqual(
            tct.interviewer_names,
            self.sample_content['transcript']['interviewer_names'])
        self.assertEqual(
            tct.transcript,
            self.sample_content['transcript']['transcript'])

    @patch('transcript.signals._delete_transcript_on_synthesis_service')
    def test_delete_user_projects_success(self, patched_signal):
        """Test deleting a user successfully deletes all their projects."""
        user = get_user_model().objects.create_user("a@b.com", 'sample123')
        Project.objects.create(title="Test Project", user=user)
        self.assertEqual(len(Project.objects.filter(user=user)), 2)

        user.delete()
        self.assertEqual(len(Project.objects.filter(user=user)), 0)
