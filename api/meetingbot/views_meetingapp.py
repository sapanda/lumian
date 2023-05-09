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

from meetingbot.errors import (
    ZoomNotIntegratedException
)

from meetingbot.models import MeetingDetails
from meetingbot.meeting_clients.zoom import (
    zoom_oauth,
    zoom_api
)

import logging

logger = logging.getLogger(__name__)

class OAuthCallbackView(APIView):

    def get(self, request):

        try:
            code = request.GET.get('code')

            # exchange authorization code for access token
            token = zoom_oauth.get_access_token(code)

            # save access and refresh tokens in database for current user
            current_user = request.user
            MeetingDetails.objects.create(
                user=current_user,
                zoom_access_token=token['access_token'],
                zoom_refresh_token=token['refresh_token'],
                meeting_url="",
                meeting_app = MeetingDetails.MeetingAppChoices.ZOOM
            )

        except Exception as e:
            logger.error(e)

        return Response({}, HTTP_202_ACCEPTED)


class MeetingDetailView(APIView):

    authentication_classes = (authentication.TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated)

    def get(self, request): # TODO: Add meetingapp as parameter as well

        try:
            user = request.user
            meeting_details = MeetingDetails.objects.get(user=user) 

            if(meeting_details):
                access_token = meeting_details.access_token
                refresh_token = meeting_details.refresh_token

                if(zoom_oauth.is_access_token_expired(access_token)):
                    new_token = zoom_oauth.refresh_access_token(refresh_token)
                    access_token = new_token['access_token']
                    refresh_token = new_token['refresh_token']
                    meeting_details.access_token = access_token
                    meeting_details.refresh_token = refresh_token
                    meeting_details.save()
                
                meetings = zoom_api.get_meetings()
                return Response(meetings)
            else:
                raise  ZoomNotIntegratedException(
                    message="Zoom is not integrated for the current user",
                    status_code=HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            message = f"HTTP error occurred: {e}"
            status_code = e.response.status_code
            logger.error(message)

        return Response(message,status_code)
