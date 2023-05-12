from django.urls import path

from meeting.views.meeting_bot import (
    AddBotView,
    BotStatusChangeView
)
from meeting.views.meeting_app import (
    OAuthCallbackView,
    MeetingDetailView
)

urlpatterns = [
     path('add-bot',
          AddBotView.as_view(), name='add-bot-to-meeting'),
     path('bot-status-change',
          BotStatusChangeView.as_view(), name='webhook-bot-status-change'),
     path('meetings',
          MeetingDetailView.as_view(), name='get-meeting-details'),
     path('access-token', OAuthCallbackView.as_view(), name='access-token')
]
