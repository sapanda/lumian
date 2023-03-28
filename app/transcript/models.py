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
    cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=0.0000)

    def __str__(self):
        return self.title


class SynthesisType(models.TextChoices):
    SUMMARY = 'SM', _('Summary')
    CONCISE = 'CS', _('Concise')


class AIChunks(models.Model):
    """Model representing a chunk of transcript."""

    class Meta:
        verbose_name = 'AI Chunks'
        verbose_name_plural = 'AI Chunks'

    transcript = models.ForeignKey(
        Transcript, on_delete=models.CASCADE)

    chunk_type = models.CharField(
        max_length=2, choices=SynthesisType.choices)
    chunks = ArrayField(models.TextField(max_length=10000))
    chunks_processed = ArrayField(models.TextField(max_length=10000))
    model_name = models.CharField(max_length=255, null=True)
    tokens_used = ArrayField(models.IntegerField())
    cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=0.0000)

    def get_chunk_type(self) -> SynthesisType:
        return dict(SynthesisType.choices).get(self.chunk_type)

    def __str__(self):
        return f'{self.get_chunk_type()} : {self.transcript.title}'


class AISynthesis(models.Model):
    """Model representing final AI synthesis of a transcript"""

    class Meta:
        verbose_name = 'AI Synthesis'
        verbose_name_plural = 'AI Syntheses'

    transcript = models.ForeignKey(
        Transcript, on_delete=models.CASCADE)

    output_type = models.CharField(
        max_length=2, choices=SynthesisType.choices)
    output = models.TextField(
        max_length=100000, blank=True, null=True)
    model_name = models.CharField(max_length=255, null=True)
    tokens_used = models.IntegerField()
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=0.0000)

    def get_synthesis_type(self) -> SynthesisType:
        return dict(SynthesisType.choices).get(self.output_type)

    def _get_short_desc(self) -> str:
        if len(self.output) < 50:
            return self.output
        return self.output[:50] + '...'

    def __str__(self):
        return f'{self.get_synthesis_type()} : {self._get_short_desc()}'


class AIEmbeds(models.Model):
    """Model representing vector embeds of a transcript"""

    class Meta:
        verbose_name = 'AI Embeds'
        verbose_name_plural = 'AI Embeds'

    transcript = models.ForeignKey(
        Transcript, on_delete=models.CASCADE)

    chunks = ArrayField(models.TextField(max_length=10000))
    pinecone_ids = ArrayField(models.CharField(max_length=255))
    index_cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=0.0000)

    def __str__(self):
        return f'{self.transcript}'


class Query(models.Model):
    """Model representing a query for a transcript"""

    class Meta:
        verbose_name = 'Query'
        verbose_name_plural = 'Queries'

    transcript = models.ForeignKey(
        Transcript, on_delete=models.CASCADE)

    query = models.TextField(max_length=10000)
    result = models.TextField(max_length=10000)
    search_values = ArrayField(models.TextField(max_length=10000))
    search_scores = ArrayField(models.DecimalField(
        max_digits=10, decimal_places=4, default=0.0000))
    query_cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=0.0000)

    def __str__(self):
        return f'{self.query}'


class Synthesis(models.Model):
    """Model representing final AI synthesis of a transcript"""

    class Meta:
        verbose_name = 'Synthesis'
        verbose_name_plural = 'Syntheses'

    transcript = models.ForeignKey(
        Transcript, on_delete=models.CASCADE)

    output_type = models.CharField(max_length=2, choices=SynthesisType.choices)
    output = models.JSONField(blank=True)
    cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=0.0000, editable=False)

    def get_synthesis_type(self) -> SynthesisType:
        return dict(SynthesisType.choices).get(self.output_type)

    @property
    def summary(self) -> str:
        return ''.join([item["text"] for item in self.output])

    @property
    def reverse_lookups(self) -> str:
        text = self.transcript.transcript
        result = []
        n = len(self.output)
        for i in range(n):
            item = self.output[i]
            sentence, references = item["text"], item["references"]
            result.extend((f"\n\n{i}: ", sentence, "\nReferences: "))
            for j in range(len(references)):
                reference = references[j]
                result.extend(("\n --->", text[reference[0]:reference[1]]))
        return ''.join(result)

    def __str__(self):
        return f'{self.transcript.title} {self.get_synthesis_type()}'
