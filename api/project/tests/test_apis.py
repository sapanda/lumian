"""
Tests for project management via the API.
"""
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from project.models import Project
from project.tests.utils import (
    create_user,
    create_project,
)


PROJECT_URL = reverse('project:project-list')


def detail_url(project_id):
    """Create and return a project detail URL."""
    return reverse('project:project-detail', args=[project_id])


class PublicAPITests(APITestCase):
    """Test unauthenticated API requests."""

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(PROJECT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITests(APITestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client.force_authenticate(user=self.user)

    def test_create_project_success(self):
        """Test creating a project is successful."""
        payload = {
            'title': 'Test Title',
            'questions': ['Test Q1', 'Test Q2'],
        }
        res = self.client.post(PROJECT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        pjt = Project.objects.get(id=res.data['data']['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(pjt, k), v)

    def test_create_project_failure(self):
        """Test creating a project with bad inputs is unsuccessful."""
        payload = {
            'title': '',
            'questions': [],
        }
        res = self.client.post(PROJECT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['title'][0],
                         'This field may not be blank.')
        self.assertTrue('questions' not in res.data,
                        'questions param can be left blank.')

    def test_retrieve_projects(self):
        """Test retrieving projects for current user only."""
        other_user = create_user(email='other@example.com', password='test123')
        other_project = create_project(user=other_user)
        create_project(user=self.user)
        create_project(user=self.user)
        create_project(user=self.user)

        res = self.client.get(PROJECT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['data']), 4)  # 3 + sample project
        self.assertFalse(any(item['id'] == other_project.id
                             for item in res.data['data']),
                         "Wrong project returned for user")

    def test_patch_project_success(self):
        """Test updating the project metadata is successful."""
        pjt = create_project(user=self.user)
        old_questions = pjt.questions
        payload = {'title': 'Even Newer Title'}
        url = detail_url(pjt.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        pjt.refresh_from_db()
        self.assertEqual(pjt.title, payload['title'])
        self.assertEqual(pjt.questions, old_questions)

    def test_patch_project_failure(self):
        """Test updating another user's project metadata fails."""
        other_user = create_user(email='other@example.com', password='test123')
        pjt = create_project(user=other_user)
        old_title = pjt.title
        payload = {'title': 'Even Newer Title'}
        url = detail_url(pjt.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        pjt.refresh_from_db()
        self.assertEqual(pjt.title, old_title)

    def test_delete_project_success(self):
        """Test deleting the project is successful."""
        pjt = create_project(user=self.user)

        url = detail_url(pjt.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(Project.objects.filter(id=pjt.id).exists())

    def test_delete_project_failure(self):
        """Test deleting another user's project fails."""
        other_user = create_user(email='user2@example.com', password='test123')
        other_project = create_project(user=other_user)

        url = detail_url(other_project.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Project.objects.filter(id=other_project.id).exists())
