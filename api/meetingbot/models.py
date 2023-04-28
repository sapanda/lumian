from django.db import models
from django.conf import settings
from transcript.models import Transcript

class MeetingBot(models.Model):

    class StatusChoices(models.TextChoices):
        READY = 'ready', 'The bot is ready to join the call'
        JOINING_CALL = 'joining_call', 'The bot has acknowledged the request to join the call, and is in the process of connecting.'
        IN_WAITING_ROOM = 'in_waiting_room', 'The bot is in the waiting room of the meeting.'
        IN_CALL_NOT_RECORDING = 'in_call_not_recording', 'The bot has joined the meeting, however is not recording yet.'
        IN_CALL_RECORDING = 'in_call_recording', 'The bot is in the meeting, and is currently recording the audio and video.'
        CALL_ENDED = 'call_ended', 'The bot has left the call, and the real-time transcription is complete.'
        DONE = 'done', 'The video is uploaded and available for download.'
        FATAL = 'fatal', 'The bot has encountered an error that prevented it from joining the call.'
        ANALYSIS_DONE = 'analysis_done', 'Any asynchronous intelligence has been completed.'

    bot_id = models.CharField(max_length=255,primary_key=True)
    status = models.CharField(max_length=32, choices=StatusChoices.choices)
    message = models.CharField(max_length=1024, null=True)
    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)


