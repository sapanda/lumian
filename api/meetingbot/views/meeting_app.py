from rest_framework.status import (
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView
from rest_framework.response import Response

from meetingbot.errors import (
    ZoomOauthException,
    ZoomAPIException
)

from meetingbot.models import MeetingAppDetails
from meetingbot.external_clients.zoom import (
    ZoomOAuth,
    ZoomAPI
)
from meetingbot.serializers import (
    OauthCallbackSerializer
)

import logging
logger = logging.getLogger(__name__)


class OAuthCallbackView(APIView):

    serializer_class = OauthCallbackSerializer

    def get(self, request):
        try:
            serializer = self.serializer_class(data=request.GET)
            if (not serializer.is_valid()):
                logger.error(f"-- Serialization Error -- {serializer.errors}")
                return Response({}, HTTP_202_ACCEPTED
                                )
            oauth = ZoomOAuth()
            token = oauth.get_access_token(serializer.validated_data['code'])

            access_token = token.get('access_token')
            refresh_token = token.get('refresh_token')
            user_email = ZoomAPI(access_token).get_user().get('email')

            MeetingAppDetails.objects.create(
                user_email=user_email,
                access_token=access_token,
                refresh_token=refresh_token,
                meeting_app=MeetingAppDetails.MeetingAppChoices.ZOOM
            )

        except Exception as e:
            logger.error(f"-- Exception : {str(e)} --")

        return Response({}, HTTP_202_ACCEPTED)


class MeetingDetailView(APIView):

    def get(self, request):
        try:
            user_email = request.query_params.get('user_email')
            meeting_app = request.query_params.get('meeting_app')
            meeting_app_details = MeetingAppDetails.objects.get(
                user_email=user_email,
                meeting_app=meeting_app
            )

            # TODO : Add check for meeting app type and initialize accordingly
            oauth = ZoomOAuth()
            access_token = meeting_app_details.access_token
            refresh_token = meeting_app_details.refresh_token

            if (oauth.is_access_token_expired(access_token)):
                new_token = oauth.refresh_access_token(refresh_token)
                access_token = new_token['access_token']
                refresh_token = new_token['refresh_token']
                meeting_app_details.access_token = access_token
                meeting_app_details.refresh_token = refresh_token
                meeting_app_details.save()

            meeting_api = ZoomAPI(access_token)
            meetings = meeting_api.get_meetings().get('meetings')
            meeting_urls = [meet.get('join_url') for meet in meetings]

            return Response(meeting_urls)

        except MeetingAppDetails.DoesNotExist:
            message = "Meeting details not found"
            status_code = HTTP_404_NOT_FOUND
        except ZoomOauthException as e:
            message = str(e)
            status_code = HTTP_401_UNAUTHORIZED
        except ZoomAPIException as e:
            message = str(e)
            status_code = HTTP_403_FORBIDDEN
        except Exception as e:
            message = f" Error occurred: {str(e)}"
            status_code = HTTP_400_BAD_REQUEST

        logger.error(f"-- Exception : {message} --")
        return Response(message, status_code)
