from django.contrib import admin

from meeting.models import (
    MeetingBot,
    MeetingApp,
    MeetingCalendar
)

admin.site.register(MeetingBot)
admin.site.register(MeetingApp)
admin.site.register(MeetingCalendar)
