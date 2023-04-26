from django.db import models

from transcript.models import Transcript

class MeetingBot(models.Model):
    status = models.CharField(max_length=20)
    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE)

