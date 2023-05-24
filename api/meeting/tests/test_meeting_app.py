from unittest import mock
from meeting.errors import ZoomException
from rest_framework.test import APITestCase
from rest_framework import status
from meeting.models import MeetingApp
from django.urls import reverse
from meeting.tests.utils import create_user
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED
)


class OAuthCallbackViewTest(APITestCase):

    def setUp(self):
        self.url = reverse('save-access-token')
        self.user = create_user()

    def tearDown(self):
        self.user.delete()

    @mock.patch('meeting.views.meeting_app.zoom_api')
    def test_valid_oauth_callback(self, mock_zoom_api):
        self.client.force_authenticate(user=self.user)
        mock_token = {
            'access_token': 'access_token',
            'refresh_token': 'refresh_token'
            }
        mock_user = {
            'email': 'user@example.com'
        }
        mock_zoom_api.get_access_token.return_value = mock_token
        mock_zoom_api.get_user.return_value = mock_user

        data = {
            "code": "valid"
        }
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        meeting_app = MeetingApp.MeetingAppChoices.ZOOM
        self.assertTrue(MeetingApp.objects.filter(
                            user=self.user,
                            meeting_email='user@example.com',
                            access_token='access_token',
                            refresh_token='refresh_token',
                            meeting_app=meeting_app).exists())

    @mock.patch('meeting.views.meeting_app.zoom_api')
    def test_invalid_oauth_callback(self, mock_zoom_api):
        self.client.force_authenticate(user=self.user)
        mock_zoom_api.get_access_token.side_effect = \
            Exception('Invalid code')

        data = {
            "code": "invalid"
        }
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(MeetingApp.objects.exists())


class MeetingDetailViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('get-meeting-details')
        self.user = create_user()
        self.meeting_app = MeetingApp.objects.create(
            user=self.user,
            access_token="access_token",
            refresh_token="refresh_token",
            meeting_app=MeetingApp.MeetingAppChoices.ZOOM,
            meeting_email="test@example.com"
        )
        self.join_url = 'https://example.com/123456'
        self.meeting_app_choice = MeetingApp.MeetingAppChoices.ZOOM
        self.meeting_email = 'test@example.com'

    @mock.patch('meeting.views.meeting_app.zoom_api')
    def test_get_meeting_details(self, mock_zoom_api):
        self.client.force_authenticate(self.user)
        meetings = {'meetings': [{'join_url': self.join_url}]}
        mock_zoom_api.get_meetings.return_value = meetings
        mock_zoom_api.is_access_token_expired.return_value = False
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [self.join_url])

    @mock.patch('meeting.views.meeting_app.zoom_api')
    def test_access_token_expired(
        self,
        mock_zoom_api,
    ):
        self.client.force_authenticate(self.user)
        meetings = {'meetings': [{'join_url': self.join_url}]}
        mock_zoom_api.get_meetings.return_value = meetings
        mock_zoom_api.is_access_token_expired.return_value \
            = True
        mock_zoom_api.refresh_access_token.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token'
        }
        response = self.client.get(self.url)
        self.meeting_app.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.meeting_app.access_token, 'new_access_token')
        self.assertEqual(self.meeting_app.refresh_token, 'new_refresh_token')
        self.assertEqual(response.json(), [self.join_url])


class OAuthViewTest(APITestCase):

    def setUp(self):
        self.url = reverse('get-oauth-url')
        self.user = create_user()

    def tearDown(self):
        self.user.delete()

    @mock.patch('meeting.views.meeting_app.zoom_api.get_oauth_url')
    def test_get_oauth_url(self, mock_get_oauth_url):
        mock_get_oauth_url.return_value = 'https://example.com'
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'https://example.com')

    @mock.patch('meeting.views.meeting_app.zoom_api.get_oauth_url')
    def test_zoom_exception_handling(self, mock_get_oauth_url):
        mock_get_oauth_url.side_effect = ZoomException(
                'Zoom API exception',
                HTTP_401_UNAUTHORIZED
            )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, 'Zoom API exception')
