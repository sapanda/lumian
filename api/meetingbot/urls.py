from django.urls import path

from meetingbot.views import CreatBotView, BotStatusChangeView

urlpatterns = [
    path('add',CreatBotView.as_view(),name='add-bot-to-meeting'),
    path('webhook',BotStatusChangeView.as_view(), name='webhook-bot-status-change')
]