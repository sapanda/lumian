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
        try:
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
                        transcript = None,
                        message = "Bot is created and ready to join the call"
                    )
                else:
                    response_data = {"error": "Failed to add bot to meeting"}
                    response_status = status.HTTP_400_BAD_REQUEST
            else:
                response_data = serializer.errors
                response_status = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            response_data = {"error": str(e)}
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(response_data, status=response_status)


# View for callback URL for every bot status change
class BotStatusChangeView(APIView):

    serializer_class = BotStatusChangeSerializer

    def _update_bot(self, bot_id, status, message = "" , transcript = None):

        meetingbot = MeetingBot.objects.get(bot_id=bot_id)
        meetingbot.status = status
        meetingbot.message = message
        meetingbot.transcript = transcript
        meetingbot.save()

    def _create_transcript(self, bot_id):

        # Change this for API admin user
        User = get_user_model()
        dummy_user = User.objects.get(name="dummy_user")

        transcript_list = get_meeting_transcript_list(bot_id)
        transcript_text = transcript_utils.generate_transcript_text(transcript_list)

        return Transcript.objects.create(
            user=dummy_user,
            transcript=transcript_text,
            title="Meeting transcript",
            interviewee_names=["Ashutosh"],
            interviewer_names=["Saswat"]
        )


    def post(self, request):

        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                logger.error(f"---- Error ---- {serializer.errors}")
                return Response({}, status.HTTP_202_ACCEPTED)

            data = serializer.validated_data['data']
            status_code = data['status']['code']
            status_message = data['status']['message']
            bot_id = data['bot_id']

            # get the transcript if the status is done
            transcript = None
            if status_code == 'done':
                transcript = self._create_transcript(bot_id)

            # change status of the bot on each callback
                self._update_bot(bot_id, status_code, status_message)

        except Exception as e:
            logger.error(f"---- Error ---- {str(e)}")

        return Response({}, status.HTTP_202_ACCEPTED)
        


# TODO : 
# 1. Multi user testing and accuracy of transcript_text() utility function
# 2. Unit testing
# 3. User management for callback
# 4. Figuring out interviewee and interviewer 
# 5. Dynamically creating Title