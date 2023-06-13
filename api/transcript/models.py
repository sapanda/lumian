from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _


def _citations_from_output(transcript: str, output: str):
    text = transcript
    result = []
    n = len(output)
    for i in range(n):
        item = output[i]
        sentence, references = item["text"], item["references"]
        result.extend((f"{i}: ", sentence, "\nReferences: "))
        for j in range(len(references)):
            reference = references[j]
            result.extend(("\n ---> ", text[reference[0]:reference[1]]))
        result.extend("\n\n")
    return ''.join(result)


class Transcript(models.Model):
    """Model representing a transcript and corresponding AI synthesis."""

    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    interviewee_names = ArrayField(
        models.CharField(max_length=255), default=list)
    interviewer_names = ArrayField(
        models.CharField(max_length=255), default=list)
    transcript = models.TextField(
        max_length=100000, blank=True, null=True)
    metadata_generated = models.BooleanField(default=False)
    cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=0.0000)

    def __str__(self):
        return self.title


class SynthesisType(models.TextChoices):
    SUMMARY = 'SM', _('Summary')
    CONCISE = 'CS', _('Concise')


class SynthesisStatus(models.TextChoices):
    NOT_STARTED = 'NS', _('Not Started')
    IN_PROGRESS = 'IP', _('In Progress')
    COMPLETED = 'C', _('Completed')
    FAILED = 'F', _('Failed')


class Synthesis(models.Model):
    """Model representing final synthesis of a transcript"""

    class Meta:
        verbose_name = 'Synthesis'
        verbose_name_plural = 'Syntheses'

    transcript = models.ForeignKey(
        Transcript, on_delete=models.CASCADE)

    output_type = models.CharField(max_length=2, choices=SynthesisType.choices)
    output = models.JSONField(blank=True, null=True)
    prompt = models.TextField(max_length=20000, blank=True, null=True)
    cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=0.0000, editable=False)
    status = models.CharField(max_length=2, choices=SynthesisStatus.choices,
                              default=SynthesisStatus.NOT_STARTED)

    def get_synthesis_type(self) -> SynthesisType:
        return dict(SynthesisType.choices).get(self.output_type)

    @property
    def synthesis(self) -> str:
        if self.output:
            if self.output_type == SynthesisType.SUMMARY:
                return ''.join([item["text"] for item in self.output])
            elif self.output_type == SynthesisType.CONCISE:
                return '\n'.join([item["text"] for item in self.output])
            return 'Invalid synthesis type'
        return ''

    @property
    def citations(self) -> str:
        return _citations_from_output(self.transcript.transcript, self.output)

    def __str__(self):
        return f'{self.transcript.title} {self.get_synthesis_type()}'


class Embeds(models.Model):
    """Model representing simplified embeds metadata for a transcript"""

    class Meta:
        verbose_name = 'Embeds'
        verbose_name_plural = 'Embeds'

    transcript = models.ForeignKey(
        Transcript, on_delete=models.CASCADE)

    cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=0.0000, editable=False)
    status = models.CharField(max_length=2, choices=SynthesisStatus.choices,
                              default=SynthesisStatus.NOT_STARTED)

    def __str__(self):
        return f'{self.transcript}'


class Query(models.Model):
    """Model representing a query for a transcript"""

    class Meta:
        verbose_name = 'Query'
        verbose_name_plural = 'Queries'

    class QueryLevelChoices(models.TextChoices):
        PROJECT = 'project', _('Project level queries')
        TRANSCRIPT = 'transcript', _('Transcript level queries')

    transcript = models.ForeignKey(
        Transcript, on_delete=models.CASCADE)

    query = models.TextField(max_length=10000)
    output = models.JSONField(blank=True)
    prompt = models.TextField(max_length=20000, blank=True)
    cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=0.0000)
    query_level = models.CharField(
        max_length=32,
        choices=QueryLevelChoices.choices)

    @property
    def synthesis(self) -> str:
        return ''.join([item["text"] for item in self.output])

    @property
    def citations(self) -> str:
        return _citations_from_output(self.transcript.transcript, self.output)

    def __str__(self):
        return f'{self.query}'


class StatusChoices(models.TextChoices):
    SUMMARY = 'summary', _('summary status')
    CONCISE = 'concise', _('concise status')
    QUESTION = 'question', _('project questions status')
    QUERY = 'query', _('transcript query status')
