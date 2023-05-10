"""
Tests for the Django admin modifications.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch

from project.tests.utils import (
    create_user,
    create_project
)


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
        self.project = create_project(user=self.user)

    def test_project_lists(self):
        """Test that projects are listed on page."""
        url = reverse('admin:project_project_changelist')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_edit_project_page(self):
        """Test the edit project page works."""
        url = reverse('admin:project_project_change', args=[self.project.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_project_page(self):
        """Test the create project page works."""
        url = reverse('admin:project_project_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
