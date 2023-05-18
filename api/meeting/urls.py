from django.urls import path

from meeting.views.meeting_bot import (
    AddBotView,
    BotStatusChangeView
)
from meeting.views.meeting_app import (
    OAuthView,
    OAuthCallbackView,
    MeetingDetailView
)
from meeting.views.meeting_transcript import (
    InitiateTranscription
)

urlpatterns = [
     path('add-bot',
          AddBotView.as_view(), name='add-bot-to-meeting'),
     path('bot-status-change',
          BotStatusChangeView.as_view(), name='webhook-bot-status-change'),
     path('meetings',
          MeetingDetailView.as_view(), name='get-meeting-details'),
     path('initiate-oauth',
          OAuthView.as_view(), name='initiate-oauth'),
     path('access-token',
          OAuthCallbackView.as_view(), name='callback-access-token'),
     path('initiate-transcription',
          InitiateTranscription.as_view(), name='initiate-transcription')
]

# TODO : Add following URLS :
# 1. Initiate authorization with custom url for zoom
# 2. Add URL to get bot status
