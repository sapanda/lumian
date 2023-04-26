from django.contrib.auth import get_user_model

from rest_framework import (
    authentication,
    permissions,
    status
)

from rest_framework.views import APIView
from rest_framework.response import Response

from meetingbot.recallai_client import add_bot_to_meeting, get_meeting_transcript_list
from meetingbot.serializers import CreateBotAPISerializer, BotStatusChangeSerializer
from meetingbot.utils import transcript_utils
from meetingbot.models import MeetingBot

from transcript.models import Transcript

import logging

logger = logging.getLogger(__name__)

# View for adding bot to a meeting
class CreatBotView(APIView):

    serializer_class = CreateBotAPISerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            bot_name = serializer.validated_data['bot_name']
            meeting_url = serializer.validated_data['meeting_url']
            bot_added = add_bot_to_meeting(bot_name, meeting_url)
            
            if "error" not in bot_added:
                response_data = bot_added
                response_status = status.HTTP_200_OK 
                MeetingBot.objects.create(
                    bot_id = response_data['id'],
                    status = "bot_created",
                    transcript = None
                )
            else:
                response_data = {"error": "Failed to add bot to meeting"}
                response_status = status.HTTP_400_BAD_REQUEST
        else:
            response_data = serializer.errors
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(response_data, status=response_status)


# View for callback URL for every bot status change
class BotStatusChangeView(APIView):

    serializer_class = BotStatusChangeSerializer

    def post(self, request):
        
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        status_data = serializer.validated_data['data']['status']
        bot_id = serializer.validated_data['data']['bot_id']
        meetingbot = MeetingBot.objects.get(bot_id = bot_id)

        if status_data['code'] != 'done':
            meetingbot.status = status_data['code']
            meetingbot.save()
            return Response({}, status.HTTP_202_ACCEPTED)

        transcript_list = get_meeting_transcript_list(bot_id)
        transcript_text = transcript_utils.generate_transcript_text(transcript_list)
        logger.debug(f"{transcript_text}")

        # TODO : Figure out how to do user :
        User = get_user_model()
        dummy_user = User.objects.get(name="dummy_user")

        # save transcript to the database
        transcript = Transcript.objects.create(
            user=dummy_user,
            transcript=transcript_text,
            title="Meeting transcript",
            interviewee_names = ["Ashutosh"],
            interviewer_names = ["Saswat"]
        )

        meetingbot.status = status_data['code']
        meetingbot.transcript = transcript
        meetingbot.save()

        return Response({}, status.HTTP_202_ACCEPTED)
        
