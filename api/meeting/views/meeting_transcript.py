import requests
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
)
from rest_framework import (
    authentication,
    permissions
)
from rest_framework.views import APIView
from rest_framework.response import Response

from meeting.views.meeting_app import MeetingDetailView
from meeting.views.meeting_bot import AddBotView
from meeting.serializers import InitiateTranscriptionSerializer

import logging
logger = logging.getLogger(__name__)


class InitiateTranscription(APIView):

    serializer_class = InitiateTranscriptionSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def _get_meeting_list(self, request):
        url = reverse('get-meeting-details', request=request)
        headers = {'Authorization': f'Token {request.auth}'}
        response = requests.get(url, headers=headers)
        if response.status_code // 100 != 2:
            status = response.status_code
            message = response.text
            logger.error(f'Request failed {status}: {message}')
            response.raise_for_status()
        return response.json()

    def _add_bot_to_meetings(self, request, meetings, project_id, bot_name):
        url = reverse('add-bot-to-meeting', request=request)
        headers = {'Authorization': f'Token {self.request.auth}'}
        for meeting in meetings:
            data = {
                'meeting_url': meeting,
                'project_id': project_id,
                'bot_name': bot_name
            }
            response = requests.post(url, headers=headers, data=data)
            if response.status_code // 100 != 2:
                status = response.status_code
                message = response.text
                logger.error(f'Request failed {status}: {message}')
                response.raise_for_status()
            logger.debug(response.json())

    def post(self, request):

        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, HTTP_400_BAD_REQUEST)

            project_id = serializer.validated_data['project_id']

            meetings = self._get_meeting_list(request)
            self._add_bot_to_meetings(request, meetings, project_id, "DEFAULT")
            return Response("Bot added to the Meeting", HTTP_200_OK)
        
        except Exception as e:
            return Response(str(e))

