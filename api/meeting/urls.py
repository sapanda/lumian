from django.urls import path

from meeting.views.meeting_bot import (
    AddBotView,
    BotStatusChangeView,
    GetBotStatusView
)
from meeting.views.meeting_app import (
    OAuthView,
    OAuthCallbackView,
    MeetingDetailView
)
from meeting.views.meeting_transcript import (
    InitiateTranscription
)

from meeting.views.meeting_calendar import (
    OAuthRequestView,
    OAuthResponseView,
    EventDetailsView
)

urlpatterns = [
     path('bot/add',
          AddBotView.as_view(), name='add-bot-to-meeting'),
     path('bot/status/update',
          BotStatusChangeView.as_view(), name='webhook-bot-status-change'),
     path('bot/status',
          GetBotStatusView.as_view(), name='get-bot-status'),
     path('app/oauth-request',
          OAuthView.as_view(), name='app-oauth-request-url'),
     path('app/access-token',
          OAuthCallbackView.as_view(), name='app-oauth-response-token'),
     path('app/meetings',
          MeetingDetailView.as_view(), name='app-meeting-details'),
     path('calendar/oauth-request',
          OAuthRequestView.as_view(), name='calendar-oauth-request-url'),
     path('calendar/oauth-response',
          OAuthResponseView.as_view(), name='calendar-oauth-response-token'),
     path('calendar/meetings',
          EventDetailsView.as_view(), name='calendar-meeting-details'),
     path('initiate-transcription',
          InitiateTranscription.as_view(), name='initiate-transcription')

]
