from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    """Model representing a project."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    questions_list = ArrayField(
        models.CharField(max_length=10000), default=list)

    def __str__(self):
        return self.title
