from django.db import models
from django.utils.translation import gettext as _
from django.conf import settings


class MeetingBot(models.Model):

    class StatusChoices(models.TextChoices):
        READY = 'ready', _('Ready')
        JOINING_CALL = 'joining_call', _('Joining call')
        IN_WAITING_ROOM = 'in_waiting_room', _('In waiting room')
        IN_CALL_NOT_RECORDING = 'in_call_not_recording', _('Not recording')
        IN_CALL_RECORDING = 'in_call_recording', _('Call recording')
        CALL_ENDED = 'call_ended', _('Transcription Complete')
        DONE = 'done', _('Video available for download')
        FATAL = 'fatal', _('Error')
        ANALYSIS_DONE = 'analysis_done', _('Async Intelligence done')

    id = models.CharField(max_length=255, primary_key=True)
    status = models.CharField(max_length=32, choices=StatusChoices.choices)
    message = models.TextField(null=True)
    meeting_url = models.TextField()
    start_time = models.DateTimeField(null=True, blank=True, default=None)
    end_time = models.DateTimeField(null=True, blank=True, default=None)
    transcript = models.ForeignKey(
        "transcript.Transcript",
        on_delete=models.CASCADE,
        null=True)
    project = models.ForeignKey(
        "project.Project",
        on_delete=models.CASCADE)


class MeetingCalendar(models.Model):

    class CalendarChoices(models.TextChoices):
        GOOGLE = 'google', _('Google Calendar')
        # TODO : add other meeting choices

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    calendar_app = models.CharField(
        max_length=32,
        choices=CalendarChoices.choices)
    calendar_id = models.CharField(max_length=512)
    calendar_email = models.EmailField(max_length=512)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['calendar_email', 'calendar_app'],
                                    name='unique_calendar_details')
        ]

    def __str__(self):
        return f'{self.user.id}: {self.calendar_email}'
