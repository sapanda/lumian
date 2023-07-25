from django.db import models


class ProcessedTranscript(models.Model):
    """Model for storing processed transcripts"""

    class Meta:
        verbose_name = "Processed Transcript"
        verbose_name_plural = "Processed Transcripts"

    transcript = models.ForeignKey(
        'transcript.transcript',
        on_delete=models.CASCADE,
    )
    data = models.JSONField()

    @property
    def indexed(self) -> str:
        return '\n'.join([
            f"[{i}] {self.data[i]['text']}" for i in range(len(self.data))
        ])

    def __str__(self):
        return f'[{self.transcript.project.title}] {self.transcript.title}'
