"""
Tests for the Django admin modifications.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch

from transcript.tests.utils import create_user, create_transcript


@patch('transcript.signals._run_generate_synthesis')
class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )
        self.client.force_login(self.admin_user)

        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )

        self.tpt = create_transcript(self.user)

    def test_transcript_lists(self, patched_signal):
        """Test that transcripts are listed on page."""
        url = reverse('admin:transcript_transcript_changelist')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_edit_transcript_page(self, patched_signal):
        """Test the edit transcript page works."""
        url = reverse('admin:transcript_transcript_change', args=[self.tpt.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_transcript_page(self, patched_signal):
        """Test the create transcript page works."""
        url = reverse('admin:transcript_transcript_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    # TODO: Test that AISynthesis, AIChunks, AIEmbed, and Query are listed
