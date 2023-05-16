import json
from django.contrib.auth import get_user_model
from rest_framework.status import (
    HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError,
    NotFound,
)
from rest_framework import (
    authentication,
    permissions
)
from meeting.errors import (
    ZoomOauthException,
    ZoomAPIException
)
from meeting.models import MeetingApp
from meeting.external_clients.zoom import (
    ZoomOAuth,
    ZoomAPI
)
from meeting.serializers import (
    OauthCallbackSerializer,
    MeetingDetailsSerializer
)

import logging
logger = logging.getLogger(__name__)
User = get_user_model()


class OAuthCallbackView(APIView):

    serializer_class = OauthCallbackSerializer

    def _get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound(f"User Not Found with user id {user_id}")

    def get(self, request):
        try:
            serializer = self.serializer_class(data=request.GET)
            if (not serializer.is_valid()):
                logger.error(f"-- Serialization Error -- {serializer.errors}")
                return Response({}, HTTP_202_ACCEPTED)
            
            state = json.loads(serializer.validated_data['state'])
            user = self._get_user(state['user_id'])

            oauth = ZoomOAuth()
            token = oauth.get_access_token(serializer.validated_data['code'])
            access_token = token.get('access_token')
            refresh_token = token.get('refresh_token')
            
            meeting_email = ZoomAPI(access_token).get_user().get('email')

            MeetingApp.objects.create(
                user=user,
                meeting_email=meeting_email,
                access_token=access_token,
                refresh_token=refresh_token,
                meeting_app=MeetingApp.MeetingAppChoices.ZOOM
            )

        except Exception as e:
            logger.error(f"-- Exception : {str(e)} --")

        return Response({}, HTTP_202_ACCEPTED)


class MeetingDetailView(APIView):

    serializer_class = MeetingDetailsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            meeting_app_details = MeetingApp.objects.get(
                user=request.user
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

        except MeetingApp.DoesNotExist:
            message = "Meeting details not found"
            status_code = HTTP_404_NOT_FOUND
        except ValidationError as e:
            message = str(e)
            status_code = HTTP_400_BAD_REQUEST
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
