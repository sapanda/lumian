from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _


class Transcript(models.Model):
    """Model representing a transcript and corresponding AI synthesis."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    interviewee_names = ArrayField(
        models.CharField(max_length=255), default=list)
    interviewer_names = ArrayField(
        models.CharField(max_length=255), default=list)
    transcript = models.TextField(
        max_length=100000, blank=True, null=True)
    summary = models.OneToOneField(
        'AISynthesis', on_delete=models.SET_NULL,
        related_name='transcript', blank=True, null=True)

    def __str__(self):
        return self.title


class AISynthesis(models.Model):
    """Generic class for AI synthesis model."""

    class Meta:
        verbose_name = 'AI Synthesis'
        verbose_name_plural = 'AI Syntheses'

    class SynthesisType(models.TextChoices):
        SUMMARY = 'SM', _('Summary')
        HIGHLIGHTS = 'HL', _('Highlights')
        CONCISE = 'CS', _('Concise')

    output_type = models.CharField(
        max_length=2, choices=SynthesisType.choices)
    output = models.TextField(max_length=100000, blank=True, null=True)

    def get_synthesis_type(self) -> SynthesisType:
        return self.SynthesisType[self.output_type]

    def __get_short_desc(self) -> str:
        if len(self.output) < 50:
            return self.output
        return self.output[:50] + '...'

    def __str__(self):
        return self.__get_short_desc()
