from django.urls import path

from meetingbot.views import CreatBotView

urlpatterns = [
    path('add',CreatBotView.as_view(),name='add-bot-to-meeting')
]