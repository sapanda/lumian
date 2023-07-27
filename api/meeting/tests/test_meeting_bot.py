from django.urls import reverse
from django.db import IntegrityError

from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from meeting.errors import RecallAITimeoutException
from meeting.models import MeetingBot, MeetingCalendar
from meeting.tests.utils import (
    create_user,
    create_bot,
    create_project
)


class AddBotViewTest(APITestCase):

    def setUp(self):
        self.url = reverse('add-bot-to-meeting')
        self.user = create_user()

    @patch('meeting.views.meeting_bot.add_bot_to_meeting')
    def test_add_bot_success(self, mock_add_bot_to_meeting):
        mock_add_bot_to_meeting.return_value = \
            {
                'id': 1,
                'name': 'bot1',
                'meeting_metadata':
                    {'title': 'test'},
                'calendar_meetings': [{
                    'start_time': '2023-07-07T05:33:08.920Z',
                    'end_time': '2023-07-07T05:33:08.920Z'
                }]
            }
        self.project = create_project(self.user)
        self.client.force_authenticate(self.user)
        self.data = {
            'meeting_url': 'http://example.com/meeting',
            'project_id': self.project.id,
        }

        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MeetingBot.objects.count(), 1)

        bot = MeetingBot.objects.first()
        self.assertEqual(bot.id, str(1))
        self.assertEqual(bot.status, MeetingBot.StatusChoices.READY)
        self.assertIsNone(bot.transcript)

    @patch('meeting.views.meeting_bot.add_bot_to_meeting')
    def test_add_bot_already_exists(self, mock_add_bot_to_meeting):
        self.project = create_project(self.user)
        mock_add_bot_to_meeting.side_effect = IntegrityError
        self.project = create_project(self.user)
        self.client.force_authenticate(self.user)

        self.data = {
            'meeting_url': 'http://example.com/meeting',
            'project_id': self.project.id,
        }

        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(MeetingBot.objects.count(), 0)

    @patch('meeting.views.meeting_bot.add_bot_to_meeting')
    def test_add_bot_timeout(self, mock_add_bot_to_meeting):
        self.project = create_project(self.user)
        mock_add_bot_to_meeting.side_effect = \
            RecallAITimeoutException(
                'Timeout',
                status.HTTP_408_REQUEST_TIMEOUT
            )
        self.client.force_authenticate(self.user)

        self.data = {
            'meeting_url': 'http://example.com/meeting',
            'project_id': self.project.id,
        }

        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_408_REQUEST_TIMEOUT)
        self.assertEqual(MeetingBot.objects.count(), 0)

    @patch('meeting.views.meeting_bot.add_bot_to_meeting')
    def test_add_bot_exception(self, mock_add_bot_to_meeting):
        self.project = create_project(self.user)
        mock_add_bot_to_meeting.side_effect = ValueError('Invalid input')

        self.client.force_authenticate(self.user)

        self.data = {
            'meeting_url': 'http://example.com/meeting',
            'project_id': self.project.id,
        }

        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(MeetingBot.objects.count(), 0)


class BotStatusChangeViewTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('webhook-bot-status-change')

    @patch('meeting.views.meeting_bot.get_meeting_transcript')
    @patch('meeting.views.meeting_bot.generate_transcript_text')
    def test_successful_bot_status_update(
            self,
            mock_generate_transcript_text,
            mock_get_meeting_transcript
    ):
        self.user = create_user()
        self.project = create_project(self.user)
        self.bot = create_bot(self.project)
        data = {
            "event": "bot.status_change",
            "data": {
                "bot_id": self.bot.id,
                "status": {
                    "code": MeetingBot.StatusChoices.JOINING_CALL,
                    "message": "Bot is ready to join call",
                    "created_at": "2023-05-02T18:45:00Z"
                }
            }
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 202)
        self.bot.refresh_from_db()
        self.assertEqual(
            self.bot.status,
            MeetingBot.StatusChoices.JOINING_CALL
        )
        self.assertEqual(self.bot.message, "Bot is ready to join call")
        self.assertEqual(self.bot.transcript, None)
        mock_get_meeting_transcript.assert_not_called()
        mock_generate_transcript_text.assert_not_called()

    @patch('transcript.signals._run_generate_synthesis')
    @patch('meeting.views.meeting_bot.get_meeting_transcript')
    @patch('meeting.views.meeting_bot.generate_transcript_text')
    def test_successful_creation_of_transcript(
            self,
            mock_generate_transcript_text,
            mock_get_meeting_transcript,
            mock_generate_synthesis
    ):
        self.user = create_user()
        self.project = create_project(self.user)
        self.bot = create_bot(self.project)
        mock_generate_transcript_text.return_value = "Test"
        data = {
            "event": "bot.status_change",
            "data": {
                "bot_id": self.bot.id,
                "status": {
                    "code": MeetingBot.StatusChoices.DONE,
                    "message": "Bot is done",
                    "created_at": "2023-05-02T18:50:00Z"
                }
            }
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 202)
        self.bot.refresh_from_db()
        self.assertEqual(self.bot.status, MeetingBot.StatusChoices.DONE)
        self.assertEqual(self.bot.message, "Bot is done")
        self.assertNotEqual(self.bot.transcript, None)
        self.assertEqual(self.bot.transcript.project, self.project)


class GetBotStatusViewTest(APITestCase):

    def setUp(self):
        self.url = reverse('get-bot-status')
        self.user = create_user()
        self.project = create_project(self.user)
        self.bot = create_bot(self.project)

    def test_valid_get_request(self):
        bot_id = self.bot.id
        response = self.client.get(f"{self.url}?bot_id={bot_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['bot_status'], self.bot.status)

    def test_invalid_bot_id(self):
        invalid_bot_id = 'invalid_bot_id'
        response = self.client.get(f"{self.url}?bot_id={invalid_bot_id}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, 'Bot does not exist')


class ScheduleBotViewTests(APITestCase):

    def setUp(self):
        self.calendar_email = 'test@example.com'
        self.calendar_id = 'calendar-id-123'
        self.meeting_url = 'https://example.com/meeting'
        self.start_time = '2023-01-01T09:00:00Z'
        self.end_time = '2023-01-01T10:00:00Z'
        self.title = 'Test Meeting'

        self.user = create_user()
        self.project = create_project(self.user)
        self.calendar = MeetingCalendar.objects.create(
            user=self.user,
            calendar_email=self.calendar_email,
            calendar_app=MeetingCalendar.CalendarChoices.GOOGLE,
            calendar_id=self.calendar_id
        )

    @patch('meeting.views.meeting_bot.list_calendar_events')
    @patch('meeting.views.meeting_bot.add_bot_to_meeting')
    def test_schedule_bot_success(self,
                                  mock_add_bot_to_meeting,
                                  mock_list_calendar_events
                                  ):
        mock_list_calendar_events.return_value = [
            {
                'meeting_url': 'https://example.com/meeting',
                'start_time': '2023-06-05T10:00:00Z',
                'end_time': '2023-06-05T11:00:00Z',
                'title': 'Meeting 1'
            },
        ]
        mock_add_bot_to_meeting.return_value = {'id': 'bot_id'}
        url = reverse('add-bot-to-scheduled-meeting')
        data = {
            'calendar_email': self.calendar_email
        }

        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MeetingBot.objects.count(), 1)

    def test_schedule_bot_invalid_request(self):
        url = reverse('add-bot-to-scheduled-meeting')
        data = {}  # Invalid request data

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(MeetingBot.objects.count(), 0)

    def test_schedule_bot_exception(self):
        url = reverse('add-bot-to-scheduled-meeting')
        data = {
            'calendar_email': 'nonexistent@example.com'  # Non-existent email
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(MeetingBot.objects.count(), 0)
