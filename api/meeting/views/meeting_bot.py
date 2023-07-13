from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db import IntegrityError, transaction
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_408_REQUEST_TIMEOUT,
    HTTP_409_CONFLICT,
    HTTP_404_NOT_FOUND,
    HTTP_412_PRECONDITION_FAILED
)
from rest_framework import (
    authentication,
    permissions
)

from rest_framework.views import APIView
from rest_framework.response import Response

from meeting.external_clients.recallai import (
    add_bot_to_meeting,
    remove_bot_from_meeting,
    get_meeting_transcript,
    list_calendar_events
)
from meeting.serializers import (
    AddBotSerializer,
    BotStatusChangeSerializer,
    GetBotStatusSerializer,
    ScheduleBotSerializer
)
from meeting.utils import generate_transcript_text
from meeting.models import MeetingBot, MeetingCalendar
from meeting.errors import (
    RecallAITimeoutException,
    RecallAIException
)
from project.models import Project

from transcript.models import Transcript
from transcript.repository import create_synthesis_entry

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
                return Response({'message': serializer.errors},
                                HTTP_406_NOT_ACCEPTABLE)

            project_id = serializer.validated_data['project_id']
            meeting_url = serializer.validated_data['meeting_url']
            title = serializer.validated_data.get('title')
            start_time = serializer.validated_data.get('start_time')
            end_time = serializer.validated_data.get('end_time')
            bot_name = request.user.bot_name

            if MeetingBot.objects.filter(meeting_url=meeting_url).exists():
                return Response(
                    {'message': 'Bot already present in the meeting'},
                    HTTP_202_ACCEPTED)
            project = Project.objects.get(id=project_id)
            if not title:
                title = 'Meeting'

            bot = add_bot_to_meeting(bot_name, meeting_url)
            MeetingBot.objects.create(
                id=bot['id'],
                status=MeetingBot.StatusChoices.READY,
                message="Bot is created and ready to join the call",
                meeting_url=meeting_url,
                start_time=start_time,
                end_time=end_time,
                title=title,
                transcript=None,
                project=project
            )

            response_data = bot['id']
            response_message = f"Transcriber added to {title}"
            response_status = HTTP_201_CREATED
            return Response({'data': response_data,
                             'message': response_message},
                            status=response_status)

        except Project.DoesNotExist:
            response_message = {"error": "Project does not exist"}
            response_status = HTTP_404_NOT_FOUND
        except RecallAITimeoutException as e:
            response_message = {"error": str(e)}
            response_status = HTTP_408_REQUEST_TIMEOUT
        except RecallAIException as e:
            response_message = {"error": str(e)}
            response_status = HTTP_412_PRECONDITION_FAILED
        except IntegrityError as e:
            response_message = {"error": str(e)}
            response_status = HTTP_409_CONFLICT
        except Exception as e:
            response_message = {"error": str(e)}
            response_status = HTTP_400_BAD_REQUEST

        return Response({'message': response_message},
                        status=response_status)


class RemoveBotView(APIView):

    serializer_class = GetBotStatusSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        try:
            serializer = self.serializer_class(data=request.data)
            if (not serializer.is_valid()):
                return Response(serializer.errors, HTTP_406_NOT_ACCEPTABLE)
            bot_id = serializer.validated_data['bot_id']

            remove_bot_from_meeting(bot_id)
            return Response(
                'Transcription stopped successfully',
                HTTP_200_OK
            )

        except RecallAITimeoutException as e:
            response_data = str(e)
            response_status = HTTP_408_REQUEST_TIMEOUT
        except RecallAIException as e:
            response_data = str(e)
            response_status = HTTP_412_PRECONDITION_FAILED
        except Exception as e:
            response_data = str(e)
            response_status = HTTP_400_BAD_REQUEST
        return Response(response_data, response_status)


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

        with transaction.atomic():
            tct = Transcript.objects.create(
                project=meetingbot.project,
                transcript=transcript_text,
                title=f"Meeting transcript - {meetingbot.id}",
                interviewee_names=["Unknown"],
                interviewer_names=["Unknown"],
                start_time=meetingbot.start_time,
                end_time=meetingbot.end_time
            )

            create_synthesis_entry(tct)

        return tct

    def post(self, request):

        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                logger.exception("Serialization error",
                                 exc_info=serializer.errors)
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
                return Response(serializer.errors, HTTP_406_NOT_ACCEPTABLE)

            bot_id = serializer.validated_data['bot_id']
            bot = MeetingBot.objects.get(id=bot_id)
            data = {
                'bot_id': bot.id,
                'bot_status': bot.status,
                'meeting_title': bot.title,
                'meeting_start_time': bot.start_time,
                'meeting_end_time': bot.end_time
            }
            return Response({'data': data})
        except MeetingBot.DoesNotExist:
            response_message = "Bot does not exist"
            response_status = HTTP_404_NOT_FOUND
        except Exception as e:
            response_message = str(e)
            response_status = HTTP_400_BAD_REQUEST

        return Response(response_message,
                        response_status)


class ScheduleBotView(APIView):

    serializer_class = ScheduleBotSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                logger.exception("Serialization error while scheduling bot",
                                 exc_info=serializer.errors)
                return Response(serializer.errors, HTTP_202_ACCEPTED)

            calendar_email = serializer.validated_data['calendar_email']
            meeting_calendar_details = MeetingCalendar.objects.get(
                calendar_email=calendar_email,
                calendar_app=MeetingCalendar.CalendarChoices.GOOGLE
            )
            user = meeting_calendar_details.user
            project = Project.objects.filter(user=user).first()
            calendar_id = meeting_calendar_details.calendar_id
            events = list_calendar_events(calendar_id, schedule=True)

            for event in events:
                # TODO : How to change bot name here
                bot = add_bot_to_meeting(
                    bot_name='Lumian Notetaker',
                    meeting_url=event['meeting_url'],
                    join_at=event['start_time']
                )
                MeetingBot.objects.create(
                    id=bot['id'],
                    status=MeetingBot.StatusChoices.READY,
                    message="Bot is created and ready to join the call",
                    transcript=None,
                    project=project,
                    meeting_url=event['meeting_url'],
                    start_time=event['start_time'],
                    end_time=event['end_time'],
                    title=event['title']
                )
                logger.info(f"Bot id {bot['id']} Meeting {event['title']}")

        except MeetingCalendar.DoesNotExist:
            logger.info("MeetingCalendar does not exist")
            return Response("MeetingCalendar does not exist",
                            HTTP_202_ACCEPTED)
        except Exception as e:
            logger.info("Exception while scheduling bot")
            return Response(str(e), HTTP_202_ACCEPTED)

        return Response({}, HTTP_201_CREATED)
