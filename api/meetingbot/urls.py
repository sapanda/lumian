from django.urls import path

from meetingbot.views import CreatBotView, BotStatusChangeView


urlpatterns = [
    path('create',
         CreatBotView.as_view(), name='add-bot-to-meeting'),
    path('status/change',
         BotStatusChangeView.as_view(), name='webhook-bot-status-change')
]
