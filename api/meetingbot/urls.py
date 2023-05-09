from django.urls import path

from meetingbot.views.meeting_bot import (
    CreatBotView,
    BotStatusChangeView
)
from meetingbot.views.meeting_app import (
    OAuthCallbackView,
    MeetingDetailView
)

urlpatterns = [
     path('create',
          CreatBotView.as_view(), name='add-bot-to-meeting'),
     path('status-change',
          BotStatusChangeView.as_view(), name='webhook-bot-status-change'),
     path('meetings/<str:user_email>/<str:meeting_app>',
          MeetingDetailView.as_view(), name='meetings'),
     path('access-token', OAuthCallbackView.as_view(), name='access-token')
]
