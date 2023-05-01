from django.db import IntegrityError
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_408_REQUEST_TIMEOUT,
    HTTP_409_CONFLICT
)
from rest_framework import (
    authentication,
    permissions
)

from rest_framework.views import APIView
from rest_framework.response import Response

from meetingbot.recallai_client import (
    add_bot_to_meeting,
    get_meeting_transcript
)
from meetingbot.serializers import (
    CreateBotAPISerializer,
    BotStatusChangeSerializer
)
from meetingbot.utils import generate_transcript_text
from meetingbot.models import MeetingBot
from meetingbot.errors import RecallAITimeoutException

from transcript.models import Transcript

import logging

logger = logging.getLogger(__name__)


# View for adding bot to a meeting
class CreatBotView(APIView):

    serializer_class = CreateBotAPISerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, HTTP_400_BAD_REQUEST)

            bot_name = serializer.validated_data['bot_name']
            meeting_url = serializer.validated_data['meeting_url']

            bot = add_bot_to_meeting(bot_name, meeting_url)
            MeetingBot.objects.create(
                bot_id=bot['id'],
                status=MeetingBot.StatusChoices.READY,
                message="Bot is created and ready to join the call",
                transcript=None,
                user=request.user
            )

            response_data = bot
            response_status = HTTP_201_CREATED

        except RecallAITimeoutException as e:
            response_data = {"error": str(e)}
            response_status = HTTP_408_REQUEST_TIMEOUT
        except IntegrityError:
            response_data = {"error": "Meeting bot already exists"}
            response_status = HTTP_409_CONFLICT
        except Exception as e:
            response_data = {"error": str(e)}
            response_status = HTTP_400_BAD_REQUEST

        return Response(response_data, status=response_status)


# View for callback URL for every bot status change
class BotStatusChangeView(APIView):

    serializer_class = BotStatusChangeSerializer

    def _update_bot(self, bot_id, status, message="", transcript=None):

        meetingbot = MeetingBot.objects.get(bot_id=bot_id)
        meetingbot.status = status
        meetingbot.message = message
        meetingbot.transcript = transcript
        meetingbot.save()

    def _create_transcript(self, bot_id):

        # Change this for API admin user

        meetingbot = MeetingBot.objects.get(bot_id=bot_id)
        transcript_list = get_meeting_transcript(bot_id)
        transcript_text = generate_transcript_text(transcript_list)

        return Transcript.objects.create(
            user=meetingbot.user,
            transcript=transcript_text,
            title=f"Meeting transcript - {meetingbot.bot_id}",
            interviewee_names=["Ashutosh"],
            interviewer_names=["Saswat"]
        )

    def post(self, request):

        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                logger.error(f"---- Error ---- {serializer.errors}")
                return Response({}, HTTP_202_ACCEPTED)

            data = serializer.validated_data['data']
            status_code = data['status']['code']
            status_message = data['status']['message']
            bot_id = data['bot_id']

            # get the transcript if the status is done
            transcript = None
            if status_code == MeetingBot.StatusChoices.DONE:
                transcript = self._create_transcript(bot_id)

            # change status of the bot on each callback
            self._update_bot(bot_id, status_code, status_message, transcript)

        except Exception as e:
            logger.error(f"---- Error ---- {str(e)}")

        return Response({}, HTTP_202_ACCEPTED)

# TODO :
#  Unit testing
#  AI Generated intervieww, interviewer and title
#  Add ngrok in the dockerfile itself
