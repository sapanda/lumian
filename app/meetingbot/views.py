from rest_framework import (
    authentication,
    permissions,
    status
)

from rest_framework.views import APIView
from rest_framework.response import Response
from meetingbot.recallai_client import add_bot_to_meeting
from meetingbot.serializers import CreateBotAPISerializer


class CreatBotView(APIView):

    serializer_class = CreateBotAPISerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            bot_name = serializer.validated_data['bot_name']
            meeting_url = serializer.validated_data['meeting_url']

            response = add_bot_to_meeting(bot_name,meeting_url)
            if response.status_code == 200:
                data = response.json()
                return Response(data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

