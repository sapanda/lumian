from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.contrib.auth import get_user_model
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_408_REQUEST_TIMEOUT,
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
from meeting.models import MeetingCalendar, MeetingBot
from meeting.external_clients.google import (
    google_api
)
from meeting.external_clients.recallai import (
    create_calendar,
    retrieve_calendar,
    list_calendar_events,
    delete_calendar
)
from meeting.serializers import (
    OAuthSerializer,
    OauthCallbackSerializer,
    MeetingDetailsSerializer,
    CalendarStatusSerializer
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
            return Response({'data': url})
        except GoogleAPIException as e:
            return Response(str(e), HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), HTTP_404_NOT_FOUND)


class OAuthResponseView(APIView):

    serializer_class = OauthCallbackSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if (not serializer.is_valid()):
                return Response(serializer.errors, HTTP_406_NOT_ACCEPTABLE)

            user = request.user
            code = serializer.validated_data['code']
            _, refresh_token = google_api.get_access_token(code)
            calendar_id = create_calendar(refresh_token)
            calendar_email = retrieve_calendar(calendar_id)
            logger.info(calendar_email)
            defaults = {
                'calendar_id': calendar_id,
            }
            MeetingCalendar.objects.update_or_create(
                user=user,
                calendar_email=calendar_email,
                calendar_app=MeetingCalendar.CalendarChoices.GOOGLE,
                defaults=defaults
            )
            return Response("Calendar successfully integrated",
                            HTTP_201_CREATED)

        except GoogleAPIException as e:
            message = str(e)
            status_code = HTTP_412_PRECONDITION_FAILED
        except RecallAITimeoutException as e:
            message = str(e)
            status_code = HTTP_408_REQUEST_TIMEOUT
        except Exception as e:
            message = str(e)
            status_code = HTTP_400_BAD_REQUEST

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
            if not events:
                return Response(
                    {'message': 'No meetings found'},
                    status=HTTP_200_OK)
            
            for event in events:
                meeting_url = event['meeting_url']
                try:
                    bot = MeetingBot.objects.get(meeting_url=meeting_url)
                    event['bot_added'] = True
                    event['bot_status'] = bot.status
                except MeetingBot.DoesNotExist:
                    event['bot_added'] = False
            return Response(events)

        except MeetingCalendar.DoesNotExist:
            message = "Calendar integration doesn't exist for this user"
            status_code = HTTP_404_NOT_FOUND
        except ValidationError as e:
            message = str(e)
            status_code = HTTP_406_NOT_ACCEPTABLE
        except RecallAITimeoutException as e:
            message = str(e)
            status_code = HTTP_408_REQUEST_TIMEOUT
        except Exception as e:
            message = f" Error occurred: {str(e)}"
            status_code = HTTP_400_BAD_REQUEST

        return Response(message, status_code)


class CalendarStatusView(APIView):

    serializer_class = CalendarStatusSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='app',
                description='calendar app (google, outlook)',
                required=True,
                type=str),
        ]
    )
    def get(self, request):

        try:
            serializer = self.serializer_class(data=request.query_params)
            if (not serializer.is_valid()):
                return Response(serializer.errors, HTTP_406_NOT_ACCEPTABLE)
            MeetingCalendar.objects.get(
                user=request.user,
                calendar_app=serializer.validated_data['app']
            )
            return Response(HTTP_200_OK)
        except MeetingCalendar.DoesNotExist:
            response_data = "Calendar not integrated"
            response_status = HTTP_404_NOT_FOUND
        except Exception as e:
            response_data = str(e)
            response_status = HTTP_400_BAD_REQUEST

        return Response(response_data, response_status)


class DeleteCalendarView(APIView):

    serializer_class = CalendarStatusSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='app',
                description='calendar app (google, outlook)',
                required=True,
                type=str),
        ]
    )
    def delete(self, request):

        try:
            serializer = self.serializer_class(data=request.query_params)
            if (not serializer.is_valid()):
                return Response(serializer.errors, HTTP_406_NOT_ACCEPTABLE)
            user = request.user
            calendar = MeetingCalendar.objects.get(
                user=user,
                calendar_app=serializer.validated_data['app']
            )
            # TODO : revoke access token
            delete_calendar(calendar.calendar_id)
            calendar.delete()
            return Response(
                'Calendar deleted successfully',
                HTTP_200_OK
            )

        except MeetingCalendar.DoesNotExist:
            response_data = "Calendar not integrated"
            response_status = HTTP_404_NOT_FOUND
        except RecallAITimeoutException as e:
            response_data = str(e)
            response_status = HTTP_408_REQUEST_TIMEOUT
        except Exception as e:
            response_data = str(e)
            response_status = HTTP_400_BAD_REQUEST
        return Response(response_data, response_status)
