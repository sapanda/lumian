from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_408_REQUEST_TIMEOUT,
    HTTP_408_REQUEST_TIMEOUT,
    HTTP_409_CONFLICT,
    HTTP_404_NOT_FOUND
)
from rest_framework.views import APIView
from rest_framework.response import Response

from meetingbot.errors import (
    ZoomOauthException,
    ZoomAPIException
)

from meetingbot.models import MeetingDetails
from meetingbot.meeting_clients.zoom import (
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
            if(not serializer.is_valid()):
                logger.error(f"-- Serialization Error -- {serializer.errors}")
                return Response({}, HTTP_202_ACCEPTED
                                )
            oauth = ZoomOAuth()
            token = oauth.get_access_token(serializer.validated_data['code'])

            access_token = token.get('access_token')
            refresh_token = token.get('refresh_token')
            user_email = ZoomAPI(access_token).get_user().get('email')

            MeetingDetails.objects.create(
                user=user_email,
                access_token=access_token,
                refresh_token=refresh_token,
                meeting_url=None,
                meeting_app = MeetingDetails.MeetingAppChoices.ZOOM
            )

        except Exception as e:
            logger.error(f"-- Exception : {str(e)} --")

        return Response({}, HTTP_202_ACCEPTED)


class MeetingDetailView(APIView):

    def get(self, request, meeting_app, user_email): 

        try:
            meeting_details = MeetingDetails.objects.get(
                user=user_email,
                meeting_app=meeting_app
            ) 

            # TODO : Add check for meeting app type and initialize accordingly
            oauth = ZoomOAuth()
            access_token = meeting_details.access_token
            refresh_token = meeting_details.refresh_token

            if(oauth.is_access_token_expired(access_token)):
                new_token = oauth.refresh_access_token(refresh_token)
                access_token = new_token['access_token']
                refresh_token = new_token['refresh_token']
                meeting_details.access_token = access_token
                meeting_details.refresh_token = refresh_token
                meeting_details.save()
            
            meeting_api = ZoomAPI(access_token)
            meetings = meeting_api.get_meetings()
            return Response(meetings)
                
        except MeetingDetails.DoesNotExist:
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
        return Response(message,status_code)
