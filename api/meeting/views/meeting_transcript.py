import requests
from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_406_NOT_ACCEPTABLE
)
from rest_framework import (
    authentication,
    permissions
)
from rest_framework.views import APIView
from rest_framework.response import Response

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
        response_list = []
        for meeting in meetings:
            data = {
                'meeting_url': meeting,
                'project_id': project_id,
                'bot_name': bot_name
            }
            response = requests.post(url, headers=headers, data=data)
            if response.status_code // 100 != 2:
                meeting_details = {
                    'bot_added': False,
                    'message': response.text
                }
            else:
                meeting_details = {
                    'bot_added': True,
                    'bot_id': response.json()
                }
            response_list.append(meeting_details)
        return response_list

    def post(self, request):

        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, HTTP_406_NOT_ACCEPTABLE)

            project_id = serializer.validated_data['project_id']

            meetings = self._get_meeting_list(request)
            message = self._add_bot_to_meetings(
                    request,
                    meetings,
                    project_id,
                    "LumianBot"
                )
            return Response(message)

        except Exception as e:
            return Response(str(e))
