from django.contrib.auth import get_user_model
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_412_PRECONDITION_FAILED
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
    GoogleAPIException,
    RecallAITimeoutException
)
from meeting.models import MeetingCalendar
from meeting.external_clients.google import (
    google_api
)
from meeting.external_clients.recallai import (
    create_calendar,
    retrieve_calendar,
    list_calendar_events
)
from meeting.serializers import (
    OAuthSerializer,
    OauthCallbackSerializer,
    MeetingDetailsSerializer,
)

import logging
logger = logging.getLogger(__name__)
User = get_user_model()


class OAuthRequestView(APIView):
    serializer_class = OAuthSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        try:
            url = google_api.get_oauth_url()
            return Response(url)
        except GoogleAPIException as e:
            logger.error(f"---Exception : {str(e)} --")
            return Response(str(e), HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"-- Exception : {str(e)} --")
            return Response(str(e), HTTP_400_BAD_REQUEST)


class OAuthResponseView(APIView):

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
            code = serializer.validated_data['code']
            _, refresh_token = google_api.get_access_token(code)
            calendar_id = create_calendar(refresh_token)
            calendar_email = retrieve_calendar(calendar_id)
            defaults = {
                'calendar_id': calendar_id,
            }
            MeetingCalendar.objects.update_or_create(
                user=user,
                calendar_email=calendar_email,
                calendar_app=MeetingCalendar.CalendarChoices.GOOGLE,
                defaults=defaults
            )
            return Response(HTTP_201_CREATED)

        except GoogleAPIException as e:
            message = str(e)
            status_code = HTTP_412_PRECONDITION_FAILED
        except RecallAITimeoutException as e:
            message = str(e)
            status_code = HTTP_401_UNAUTHORIZED
        except Exception as e:
            message = str(e)
            status_code = HTTP_400_BAD_REQUEST

        logger.error(f"-- Exception : {message} --")
        return Response(message, status_code)


class EventDetailsView(APIView):

    serializer_class = MeetingDetailsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            meeting_calendar_details = MeetingCalendar.objects.get(
                user=request.user,
                calendar_app=MeetingCalendar.CalendarChoices.GOOGLE
            )

            events = list_calendar_events(meeting_calendar_details.calendar_id)
            return Response(events)

        except MeetingCalendar.DoesNotExist:
            message = "Calendar integration doesn't exist for this user"
            status_code = HTTP_404_NOT_FOUND
        except ValidationError as e:
            message = str(e)
            status_code = HTTP_406_NOT_ACCEPTABLE
        except RecallAITimeoutException as e:
            message = str(e)
            status_code = HTTP_401_UNAUTHORIZED
        except Exception as e:
            message = f" Error occurred: {str(e)}"
            status_code = HTTP_400_BAD_REQUEST

        logger.error(f"-- Exception : {message} --")
        return Response(message, status_code)
