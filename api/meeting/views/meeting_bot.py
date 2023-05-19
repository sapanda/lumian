from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db import IntegrityError
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_408_REQUEST_TIMEOUT,
    HTTP_409_CONFLICT,
    HTTP_404_NOT_FOUND
)
from rest_framework import (
    authentication,
    permissions
)

from rest_framework.views import APIView
from rest_framework.response import Response

from meeting.external_clients.recallai import (
    add_bot_to_meeting,
    get_meeting_transcript
)
from meeting.serializers import (
    AddBotSerializer,
    BotStatusChangeSerializer,
    GetBotStatusSerializer
)
from meeting.utils import generate_transcript_text
from meeting.models import MeetingBot
from meeting.errors import RecallAITimeoutException
from project.models import Project

from transcript.models import Transcript

import logging
logger = logging.getLogger(__name__)


# View for adding bot to a meeting
class AddBotView(APIView):

    serializer_class = AddBotSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, HTTP_400_BAD_REQUEST)

            bot_name = serializer.validated_data['bot_name']
            meeting_url = serializer.validated_data['meeting_url']
            project_id = serializer.validated_data['project_id']

            # TODO : Check if a bot is already present for that meeting

            bot = add_bot_to_meeting(bot_name, meeting_url)
            project = Project.objects.get(id=project_id)
            MeetingBot.objects.create(
                id=bot['id'],
                status=MeetingBot.StatusChoices.READY,
                message="Bot is created and ready to join the call",
                transcript=None,
                project=project
            )

            response_data = bot['id']
            response_status = HTTP_201_CREATED

        except Project.DoesNotExist:
            response_data = {"error": "Project does not exist"}
            response_status = HTTP_404_NOT_FOUND
        except RecallAITimeoutException as e:
            response_data = {"error": str(e)}
            response_status = HTTP_408_REQUEST_TIMEOUT
        except IntegrityError:
            response_data = {"error": "Meeting bot already exists"}
            response_status = HTTP_409_CONFLICT
        except Exception as e:
            logger.error(e)
            response_data = {"error": str(e)}
            response_status = HTTP_400_BAD_REQUEST

        return Response(response_data, status=response_status)


# View for callback URL for every bot status change
class BotStatusChangeView(APIView):

    serializer_class = BotStatusChangeSerializer

    def _update_bot(self, bot_id, status, message="", transcript=None):

        meetingbot = MeetingBot.objects.get(id=bot_id)
        meetingbot.status = status
        meetingbot.message = message
        meetingbot.transcript = transcript
        meetingbot.save()

    def _create_transcript(self, bot_id):

        # Change this for API admin user

        meetingbot = MeetingBot.objects.get(id=bot_id)
        transcript_list = get_meeting_transcript(bot_id)
        transcript_text = generate_transcript_text(transcript_list)

        return Transcript.objects.create(
            project=meetingbot.project,
            transcript=transcript_text,
            title=f"Meeting transcript - {meetingbot.id}",
            interviewee_names=["Unknown"],
            interviewer_names=["Unknown"]
        )

    def post(self, request):

        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                logger.error(f"-- Serialization Error -- {serializer.errors}")
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
            logger.error(f"-- Exception -- {str(e)}")

        return Response({}, HTTP_202_ACCEPTED)


class GetBotStatusView(APIView):

    serializer_class = GetBotStatusSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='bot_id',
                description='bot id for the bot in the meeting',
                required=True,
                type=str),
        ]
    )
    def get(self, request):

        try:
            serializer = self.serializer_class(data=request.query_params)
            if not serializer.is_valid():
                logger.error(f"-- Serialization Error -- {serializer.errors}")
                return Response(serializer.errors, HTTP_400_BAD_REQUEST)
            bot_id = serializer.validated_data['bot_id']
            bot = MeetingBot.objects.get(id=bot_id)
            return Response(bot.status)
        except MeetingBot.DoesNotExist:
            response_data = {"error": "Bot does not exist"}
            response_status = HTTP_404_NOT_FOUND
        except Exception as e:
            response_data = str(e)
            response_status = HTTP_400_BAD_REQUEST

        return Response(response_data, response_status)