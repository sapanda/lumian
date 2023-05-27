from django.contrib import admin

from meeting.models import (
    MeetingBot,
    MeetingApp
)

admin.site.register(MeetingBot)
admin.site.register(MeetingApp)
