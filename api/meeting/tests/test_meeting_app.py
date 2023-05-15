from unittest import mock
from rest_framework.test import APITestCase
from rest_framework import status
from meeting.models import MeetingApp
from django.urls import reverse


class OAuthCallbackViewTest(APITestCase):

    def setUp(self):
        self.url = reverse('callback-access-token')
        self.valid_code = 'valid_code'
        self.invalid_code = 'invalid_code'

    @mock.patch('meeting.views.meeting_app.ZoomOAuth')
    @mock.patch('meeting.views.meeting_app.ZoomAPI')
    def test_valid_oauth_callback(self, mock_zoom_api, mock_zoom_oauth):
        access_token = 'access_token'
        refresh_token = 'refresh_token'
        meeting_email = 'user@example.com'

        mock_token = {
            'access_token': access_token,
            'refresh_token': refresh_token
            }
        mock_user = {
            'email': meeting_email
        }
        mock_zoom_oauth.return_value.get_access_token.return_value = mock_token
        mock_zoom_api.return_value.get_user.return_value = mock_user

        url = f'{self.url}?code={self.valid_code}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        meeting_app = MeetingApp.MeetingAppChoices.ZOOM
        self.assertTrue(MeetingApp.objects.filter(
                            meeting_email=meeting_email,
                            access_token=access_token,
                            refresh_token=refresh_token,
                            meeting_app=meeting_app).exists())

    @mock.patch('meeting.views.meeting_app.ZoomOAuth')
    def test_invalid_oauth_callback(self, mock_zoom_oauth):
        mock_zoom_oauth.return_value.get_access_token.side_effect = \
                                                Exception('Invalid code')

        url = f'{self.url}?code={self.invalid_code}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertFalse(MeetingApp.objects.exists())


class MeetingDetailViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('get-meeting-details')
        self.meeting_app = MeetingApp.objects.create(
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
        meetings = {'meetings': [{'join_url': self.join_url}]}
        mock_zoom_api.return_value.get_meetings.return_value = meetings
        mock_zoom_oauth.return_value.is_access_token_expired.return_value \
            = False
        data = {
            'meeting_app': self.meeting_app_choice,
            'meeting_email': self.meeting_email
        }
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [self.join_url])

    def test_meeting_details_not_found(self):
        data = {
            'meeting_app': self.meeting_app_choice,
            'meeting_email': "random@example.com"
        }
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_serializer(self):
        data = {
            'meeting_email': self.meeting_email
        }
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('meeting.views.meeting_app.ZoomOAuth')
    @mock.patch('meeting.views.meeting_app.ZoomAPI')
    def test_access_token_expired(
        self,
        mock_zoom_api,
        mock_zoom_oauth
    ):
        meetings = {'meetings': [{'join_url': self.join_url}]}
        mock_zoom_api.return_value.get_meetings.return_value = meetings
        mock_zoom_oauth.return_value.is_access_token_expired.return_value \
            = True
        mock_zoom_oauth.return_value.refresh_access_token.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token'
        }
        data = {
            'meeting_app': self.meeting_app_choice,
            'meeting_email': self.meeting_email
        }
        response = self.client.get(self.url, data=data)
        self.meeting_app.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.meeting_app.access_token, 'new_access_token')
        self.assertEqual(self.meeting_app.refresh_token, 'new_refresh_token')
