from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _

from transcript.models import Transcript


class MeetingBot(models.Model):

    class StatusChoices(models.TextChoices):
        READY = 'ready', _('Ready')
        JOINING_CALL = 'joining_call', _('Joining call')
        IN_WAITING_ROOM = 'in_waiting_room', _('In waiting room')
        IN_CALL_NOT_RECORDING = 'in_call_not_recording', _('Not recording')
        IN_CALL_RECORDING = 'in_call_recording', _('Call recording')
        CALL_ENDED = 'call_ended', 'Transcription Complete'
        DONE = 'done', 'Video available for download'
        FATAL = 'fatal', 'Error'
        ANALYSIS_DONE = 'analysis_done', 'Async Intelligence done'

    bot_id = models.CharField(max_length=255, primary_key=True)
    status = models.CharField(max_length=32, choices=StatusChoices.choices)
    message = models.CharField(max_length=1024, null=True)
    transcript = models.ForeignKey(
        Transcript,
        on_delete=models.CASCADE,
        null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
