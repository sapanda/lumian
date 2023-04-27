from django.db import models

from transcript.models import Transcript

class MeetingBot(models.Model):
    bot_id = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE, null=True)
    message = models.CharField(max_length=1024, null=True)

