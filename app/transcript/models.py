from django.db import models
from django.contrib.postgres.fields import ArrayField

class Transcript(models.Model):
    title = models.CharField(max_length=255)
    interviewee_names = ArrayField(
        models.CharField(max_length=255), default=list)
    interviewer_names = ArrayField(
        models.CharField(max_length=255), default=list)
    transcript = models.TextField(max_length=100000)
