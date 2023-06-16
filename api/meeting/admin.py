from django.contrib import admin

from meeting.models import (
    MeetingBot,
    MeetingCalendar
)

admin.site.register(MeetingBot)
admin.site.register(MeetingCalendar)
