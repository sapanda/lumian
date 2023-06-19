from django.urls import path

from meeting.views.meeting_bot import (
    AddBotView,
    BotStatusChangeView,
    GetBotStatusView,
    ScheduleBotView
)
from meeting.views.meeting_calendar import (
    OAuthRequestView,
    OAuthResponseView,
    EventDetailsView,
    CalendarStatusView
)

urlpatterns = [
     path('bot/add',
          AddBotView.as_view(), name='add-bot-to-meeting'),
     path('bot/schedule',
          ScheduleBotView.as_view(), name='add-bot-to-scheduled-meeting'),
     path('bot/status/update',
          BotStatusChangeView.as_view(), name='webhook-bot-status-change'),
     path('bot/status',
          GetBotStatusView.as_view(), name='get-bot-status'),
     path('calendar/oauth-request',
          OAuthRequestView.as_view(), name='calendar-oauth-request-url'),
     path('calendar/oauth-response',
          OAuthResponseView.as_view(), name='calendar-oauth-response-token'),
     path('calendar/meetings',
          EventDetailsView.as_view(), name='calendar-meeting-details'),
     path('calendar/status',
          CalendarStatusView.as_view(), name='calendar-meeting-details'),
]
