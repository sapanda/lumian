"""
    Admin pages for the transcript app.
"""
from django import forms
from django.contrib import admin

from transcript.models import (
    Transcript,
    ProcessedChunks,
    AISynthesis,
)


class TranscriptForm(forms.ModelForm):
    file = forms.FileField(label='Upload Transcript', required=False)

    class Meta:
        model = Transcript
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('file'):
            file_content = self.cleaned_data['file'].read().decode('utf-8')
            instance.transcript = file_content
        if commit:
            instance.save()
        return instance


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    """Admin page for the transcript model."""
    form = TranscriptForm


@admin.register(AISynthesis)
class AISynthesisAdmin(admin.ModelAdmin):
    """Admin page for the AI synthesis model."""
    readonly_fields = ['output_type', 'output', 'transcript']
    list_display = ['transcript', 'output_type']


@admin.register(ProcessedChunks)
class ProcessedChunksAdmin(admin.ModelAdmin):
    """Admin page for the AI synthesis model."""
    readonly_fields = ['para_groups', 'para_group_summaries', 'transcript']
    list_display = ['transcript']
