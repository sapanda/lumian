from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Project(models.Model):
    """Model representing a project."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    goal = models.TextField(max_length=10000, blank=True, null=True)
    questions = ArrayField(models.CharField(max_length=10000),
                           default=list, blank=True, null=True)

    def __str__(self):
        return self.title
