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
    message = models.CharField(max_length=1024, null=True)
    transcript = models.ForeignKey(
        "transcript.Transcript",
        on_delete=models.CASCADE,
        null=True)
    project = models.ForeignKey(
        "project.Project",
        on_delete=models.CASCADE)


class MeetingApp(models.Model):

    class MeetingAppChoices(models.TextChoices):
        ZOOM = 'zoom', _('Zoom meeting app')
        GOOGLE = 'google', _('Google Calendar')
        # TODO : add other meeting choices

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    meeting_email = models.EmailField(max_length=512)
    access_token = models.CharField(max_length=1024)
    refresh_token = models.CharField(max_length=1024)
    meeting_app = models.CharField(
        max_length=32,
        choices=MeetingAppChoices.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['meeting_email', 'meeting_app'],
                                    name='unique_meeting_details')
        ]

    def __str__(self):
        return f'{self.user.id}: {self.meeting_email}'
