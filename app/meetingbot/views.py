from rest_framework import (
    authentication,
    permissions,
    status
)

from rest_framework.views import APIView
from rest_framework.response import Response
from meetingbot.recallai_client import add_bot_to_meeting, get_meeting_transcript
from meetingbot.serializers import CreateBotAPISerializer, BotStatusChangeSerializer
from meetingbot.utils import TranscriptUtils

import logging

logger = logging.getLogger(__name__)

class CreatBotView(APIView):

    serializer_class = CreateBotAPISerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():

            bot_name = serializer.validated_data['bot_name']
            meeting_url = serializer.validated_data['meeting_url']

            response_data = add_bot_to_meeting(bot_name, meeting_url)
            response_status = status.HTTP_200_OK if "error" not in response_data else status.HTTP_400_BAD_REQUEST
            return Response(response_data, status=response_status)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BotStatusChangeView(APIView):

    # TODO : Add serialization validation

    def post(self, request):
        
        logger.debug(f"-------> POST Request BotStatusChange Request : {request.data}")

        status_data = request.data.status

        if status_data.code == 'done':
            logger.debug(f"-------> Status is done")
            bot_id = request.data.bot_id
            #make an external call to fetch the transcript
            transcript_list = get_meeting_transcript(bot_id)
            transcript_text = TranscriptUtils.text_from_list()
            logger.debug(transcript_text)
            # save transcript to the database
                # transcript.save()
        else:
            logger.debug(f"-------> Bot still in the meeting")

        return Response({},status.HTTP_202_ACCEPTED)
        
