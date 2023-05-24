from django.contrib.auth import get_user_model
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError
)
from rest_framework import (
    authentication,
    permissions
)
from meeting.errors import (
    ZoomException
)
from meeting.models import MeetingApp
from meeting.external_clients.zoom import (
    zoom_api
)
from meeting.serializers import (
    OAuthSerializer,
    OauthCallbackSerializer,
    MeetingDetailsSerializer,
)

import logging
logger = logging.getLogger(__name__)
User = get_user_model()


class OAuthView(APIView):
    serializer_class = OAuthSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        try:
            url = zoom_api.get_oauth_url()
            return Response(url)
        except ZoomException as e:
            logger.error(f"---Exception -- {str(e)}")
            return Response(str(e), HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response(str(e), HTTP_400_BAD_REQUEST)


class OAuthCallbackView(APIView):

    serializer_class = OauthCallbackSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if (not serializer.is_valid()):
                logger.error(f"-- Serialization Error -- {serializer.errors}")
                return Response(serializer.errors, HTTP_406_NOT_ACCEPTABLE)

            user = request.user
            token = zoom_api.get_access_token(
                    serializer.validated_data['code']
                )
            access_token = token.get('access_token')
            refresh_token = token.get('refresh_token')
            meeting_email = zoom_api.get_user(access_token).get('email')

            defaults = {
                'user': user,
                'access_token': access_token,
                'refresh_token': refresh_token,
            }
            MeetingApp.objects.update_or_create(
                meeting_email=meeting_email,
                meeting_app=MeetingApp.MeetingAppChoices.ZOOM,
                defaults=defaults
            )
            return Response(HTTP_201_CREATED)

        except ZoomException as e:
            message = str(e)
            status_code = HTTP_401_UNAUTHORIZED
        except Exception as e:
            message = str(e)
            status_code = HTTP_400_BAD_REQUEST

        return Response(message, status_code)


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
            access_token = meeting_app_details.access_token
            refresh_token = meeting_app_details.refresh_token

            if (zoom_api.is_access_token_expired(access_token)):
                new_token = zoom_api.refresh_access_token(refresh_token)
                access_token = new_token['access_token']
                refresh_token = new_token['refresh_token']
                meeting_app_details.access_token = access_token
                meeting_app_details.refresh_token = refresh_token
                meeting_app_details.save()

            meetings = zoom_api.get_meetings(access_token).get('meetings')
            meeting_urls = [meet.get('join_url') for meet in meetings]

            return Response(meeting_urls)

        except MeetingApp.DoesNotExist:
            message = "Meeting details not found"
            status_code = HTTP_404_NOT_FOUND
        except ValidationError as e:
            message = str(e)
            status_code = HTTP_406_NOT_ACCEPTABLE
        except ZoomException as e:
            message = str(e)
            status_code = HTTP_401_UNAUTHORIZED
        except Exception as e:
            message = f" Error occurred: {str(e)}"
            status_code = HTTP_400_BAD_REQUEST

        logger.error(f"-- Exception : {message} --")
        return Response(message, status_code)
