from unittest.mock import patch
from django.urls import reverse
from django.db import IntegrityError

from rest_framework import status
from rest_framework.test import APITestCase

from meetingbot.errors import RecallAITimeoutException
from meetingbot.models import MeetingBot
from meetingbot.tests.utils import create_user, create_bot


class CreateBotViewTest(APITestCase):

    def setUp(self):
        self.url = reverse('add-bot-to-meeting')
        self.user = create_user()

    def tearDown(self):
        self.user.delete()

    @patch('meetingbot.views.meeting_bot.add_bot_to_meeting')
    def test_create_bot_success(self, mock_add_bot_to_meeting):
        mock_add_bot_to_meeting.return_value = {'id': 1, 'name': 'bot1'}
        data = {
                'bot_name': 'bot1',
                'meeting_url': 'http://example.com/meeting'
               }
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MeetingBot.objects.count(), 1)

        bot = MeetingBot.objects.first()
        self.assertEqual(bot.id, str(1))
        self.assertEqual(bot.status, MeetingBot.StatusChoices.READY)
        self.assertIsNone(bot.transcript)
        self.assertEqual(bot.user, self.user)

    @patch('meetingbot.views.meeting_bot.add_bot_to_meeting')
    def test_create_bot_already_exists(self, mock_add_bot_to_meeting):
        mock_add_bot_to_meeting.side_effect = IntegrityError
        data = {
                'bot_name': 'bot1',
                'meeting_url': 'http://example.com/meeting'
               }
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(MeetingBot.objects.count(), 0)

    @patch('meetingbot.views.meeting_bot.add_bot_to_meeting')
    def test_create_bot_timeout(self, mock_add_bot_to_meeting):
        mock_add_bot_to_meeting.side_effect = \
            RecallAITimeoutException(
                'Timeout',
                status.HTTP_408_REQUEST_TIMEOUT
                )
        data = {
                'bot_name': 'bot1',
                'meeting_url': 'http://example.com/meeting'
               }
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_408_REQUEST_TIMEOUT)
        self.assertEqual(MeetingBot.objects.count(), 0)

    @patch('meetingbot.views.meeting_bot.add_bot_to_meeting')
    def test_create_bot_exception(self, mock_add_bot_to_meeting):
        mock_add_bot_to_meeting.side_effect = ValueError('Invalid input')
        data = {
                'bot_name': 'bot1',
                'meeting_url': 'http://example.com/meeting'
               }
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(MeetingBot.objects.count(), 0)


class BotStatusChangeViewTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('webhook-bot-status-change')

    @patch('meetingbot.views.meeting_bot.get_meeting_transcript')
    @patch('meetingbot.views.meeting_bot.generate_transcript_text')
    def test_successful_bot_status_update(
            self,
            mock_generate_transcript_text,
            mock_get_meeting_transcript
    ):
        self.user = create_user()
        self.bot = create_bot(self.user)
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
        self.bot.delete()
        self.user.delete()

    @patch('transcript.signals._run_generate_synthesis')
    @patch('transcript.signals._delete_transcript_on_synthesis_service')
    @patch('meetingbot.views.meeting_bot.get_meeting_transcript')
    @patch('meetingbot.views.meeting_bot.generate_transcript_text')
    def test_successful_creation_of_transcript(
            self,
            mock_generate_transcript_text,
            mock_get_meeting_transcript,
            mock_delete_on_synthesis,
            mock_generate_synthesis
    ):
        self.user = create_user()
        self.bot = create_bot(self.user)
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
        self.assertEqual(self.bot.transcript.user, self.user)
        self.bot.delete()
        self.user.delete()


# TODO : Transcript Synthesis error fix, transcript delete bug fix
