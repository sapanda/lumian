from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.contrib.auth import get_user_model
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_408_REQUEST_TIMEOUT,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_417_EXPECTATION_FAILED,
    HTTP_422_UNPROCESSABLE_ENTITY
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
    RecallAITimeoutException,
    RecallAIException,
    GoogleAPIException,
    MicrosoftAPIException
)
from meeting.models import MeetingCalendar, MeetingBot
from meeting.external_clients.calendar import (
    CalendarAPIFactory
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='app',
                description='calendar app (google, microsoft)',
                required=True,
                type=str),
        ]
    )
    def get(self, request):

        try:
            serializer = self.serializer_class(data=request.query_params)
            if (not serializer.is_valid()):
                return Response(serializer.errors, HTTP_406_NOT_ACCEPTABLE)

            calendar_app = serializer.validated_data['app']
            calendar_api = CalendarAPIFactory.get_api(calendar_app)
            url = calendar_api.get_oauth_url()
            return Response({'data': url})
        except ValueError as e:
            return Response(str(e), HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            return Response(str(e), HTTP_400_BAD_REQUEST)


class OAuthResponseView(APIView):

    serializer_class = OauthCallbackSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if (not serializer.is_valid()):
                return Response(serializer.errors, HTTP_406_NOT_ACCEPTABLE)

            # Request parameters
            user = request.user
            code = serializer.validated_data['code']
            calendar_app = serializer.validated_data['app']
            calendar_api = CalendarAPIFactory.get_api(calendar_app)

            # Calendar creation
            token, refresh_token = None, None
            try:
                token, refresh_token = calendar_api.get_access_token(code)
                calendar_id = create_calendar(refresh_token, calendar_app)
                calendar_email = retrieve_calendar(calendar_id)
            except Exception as e:
                if token:
                    calendar_api.revoke_access_token(token)
                raise e

            # Create database object
            defaults = {
                'calendar_id': calendar_id,
                'access_token': token,
                'refresh_token': refresh_token,
                'calendar_email': calendar_email,

                }
            MeetingCalendar.objects.update_or_create(
                user=user,
                calendar_app=calendar_app,
                defaults=defaults
            )
            return Response(
                "Calendar successfully integrated",
                HTTP_201_CREATED)

        except RecallAITimeoutException as e:
            message = str(e)
            status_code = HTTP_408_REQUEST_TIMEOUT
        except RecallAIException as e:
            message = str(e)
            status_code = HTTP_412_PRECONDITION_FAILED
        except ValueError as e:
            message = str(e)
            status_code = HTTP_422_UNPROCESSABLE_ENTITY
        except (GoogleAPIException, MicrosoftAPIException) as e:
            message = str(e)
            status_code = HTTP_417_EXPECTATION_FAILED
        except Exception as e:
            message = str(e)
            status_code = HTTP_400_BAD_REQUEST

        return Response({'message': message}, status_code)


class EventDetailsView(APIView):

    serializer_class = MeetingDetailsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='app',
                description='calendar app (google, microsoft)',
                required=False,
                type=str),
        ]
    )
    def get(self, request):
        try:
            serializer = self.serializer_class(data=request.query_params)
            if (not serializer.is_valid()):
                return Response(serializer.errors, HTTP_406_NOT_ACCEPTABLE)

            app_type = serializer.validated_data.get('app')

            # fetch only requested calendar events
            if app_type:
                meeting_calendar = MeetingCalendar.objects.get(
                    user=request.user,
                    calendar_app=app_type
                )
                events = list_calendar_events(
                    meeting_calendar.calendar_id
                )
            # fetch all events
            else:
                google_calendar = MeetingCalendar.objects.filter(
                    user=request.user,
                    calendar_app=MeetingCalendar.CalendarChoices.GOOGLE
                ).first()
                microsoft_calendar = MeetingCalendar.objects.filter(
                    user=request.user,
                    calendar_app=MeetingCalendar.CalendarChoices.MICROSOFT
                ).first()

                if not google_calendar and not microsoft_calendar:
                    raise NotFound()

                events = []

                if google_calendar:
                    google_events = list_calendar_events(
                        google_calendar.calendar_id
                    )
                    events.extend(google_events)

                if microsoft_calendar:
                    microsoft_events = list_calendar_events(
                        microsoft_calendar.calendar_id
                    )
                    events.extend(microsoft_events)

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

            return Response({'data': events})

        except (MeetingCalendar.DoesNotExist, NotFound):
            message = "Calendar not integrated"
            status_code = HTTP_404_NOT_FOUND
        except ValidationError as e:
            message = str(e)
            status_code = HTTP_406_NOT_ACCEPTABLE
        except RecallAITimeoutException as e:
            message = str(e)
            status_code = HTTP_408_REQUEST_TIMEOUT
        except RecallAIException as e:
            message = str(e)
            status_code = HTTP_412_PRECONDITION_FAILED
        except Exception as e:
            message = f" Error occurred: {str(e)}"
            status_code = HTTP_400_BAD_REQUEST

        return Response({'message': message}, status_code)


class CalendarStatusView(APIView):

    serializer_class = CalendarStatusSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='app',
                description='calendar app (google, microsoft)',
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
                description='calendar app (google, microsoft)',
                required=True,
                type=str),
        ]
    )
    def delete(self, request):

        try:
            serializer = self.serializer_class(data=request.query_params)
            if (not serializer.is_valid()):
                return Response(serializer.errors, HTTP_406_NOT_ACCEPTABLE)
            calendar_app = serializer.validated_data['app']
            user = request.user
            calendar_api = CalendarAPIFactory.get_api(calendar_app)
            calendar = MeetingCalendar.objects.get(
                user=user,
                calendar_app=calendar_app
            )
            if calendar.access_token:
                calendar_api.revoke_access_token(calendar.access_token)
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
        except RecallAIException as e:
            response_data = str(e)
            response_status = HTTP_412_PRECONDITION_FAILED
        except GoogleAPIException as e:
            response_data = str(e)
            response_status = HTTP_417_EXPECTATION_FAILED
        except Exception as e:
            response_data = str(e)
            response_status = HTTP_400_BAD_REQUEST
        return Response(response_data, response_status)
