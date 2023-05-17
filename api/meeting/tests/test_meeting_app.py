from unittest import mock
import urllib.parse
from rest_framework.test import APITestCase
from rest_framework import status
from meeting.models import MeetingApp
from django.urls import reverse
from meeting.tests.utils import create_user


class OAuthCallbackViewTest(APITestCase):

    def setUp(self):
        self.url = reverse('callback-access-token')
        self.user = create_user()

    def tearDown(self):
        self.user.delete()

    @mock.patch('meeting.views.meeting_app.ZoomOAuth')
    @mock.patch('meeting.views.meeting_app.ZoomAPI')
    def test_valid_oauth_callback(self, mock_zoom_api, mock_zoom_oauth):
        mock_token = {
            'access_token': 'access_token',
            'refresh_token': 'refresh_token'
            }
        mock_user = {
            'email': 'user@example.com'
        }
        mock_zoom_oauth.return_value.get_access_token.return_value = mock_token
        mock_zoom_api.return_value.get_user.return_value = mock_user

        params = {
            "code": "valid",
            "state": '{"user_id": 4}'
        }
        query_string = urllib.parse.urlencode(params)
        url = f'{self.url}?{query_string}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        meeting_app = MeetingApp.MeetingAppChoices.ZOOM
        self.assertTrue(MeetingApp.objects.filter(
                            user=self.user,
                            meeting_email='user@example.com',
                            access_token='access_token',
                            refresh_token='refresh_token',
                            meeting_app=meeting_app).exists())

    @mock.patch('meeting.views.meeting_app.ZoomOAuth')
    def test_invalid_oauth_callback(self, mock_zoom_oauth):
        mock_zoom_oauth.return_value.get_access_token.side_effect = \
            Exception('Invalid code')

        params = {
            "code": "invalid",
            "state": '{"user_id": 3}'
        }
        query_string = urllib.parse.urlencode(params)
        url = f'{self.url}?{query_string}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
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

    @mock.patch('meeting.views.meeting_app.ZoomOAuth')
    @mock.patch('meeting.views.meeting_app.ZoomAPI')
    def test_get_meeting_details(self, mock_zoom_api, mock_zoom_oauth):
        self.client.force_authenticate(self.user)
        meetings = {'meetings': [{'join_url': self.join_url}]}
        mock_zoom_api.return_value.get_meetings.return_value = meetings
        mock_zoom_oauth.return_value.is_access_token_expired.return_value \
            = False
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['meeting_urls'], [self.join_url])

    @mock.patch('meeting.views.meeting_app.ZoomOAuth')
    @mock.patch('meeting.views.meeting_app.ZoomAPI')
    def test_access_token_expired(
        self,
        mock_zoom_api,
        mock_zoom_oauth
    ):
        self.client.force_authenticate(self.user)
        meetings = {'meetings': [{'join_url': self.join_url}]}
        mock_zoom_api.return_value.get_meetings.return_value = meetings
        mock_zoom_oauth.return_value.is_access_token_expired.return_value \
            = True
        mock_zoom_oauth.return_value.refresh_access_token.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token'
        }
        response = self.client.get(self.url)
        self.meeting_app.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.meeting_app.access_token, 'new_access_token')
        self.assertEqual(self.meeting_app.refresh_token, 'new_refresh_token')
        self.assertEqual(response.json()['meeting_urls'], [self.join_url])
