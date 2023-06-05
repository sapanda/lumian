"""
    Admin pages for the transcript app.
"""
from django import forms
from django.contrib import admin

from core.admin import ReadOnlyInline
from transcript.models import (
    Transcript, Synthesis, Embeds, Query
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


class SynthesisInline(ReadOnlyInline):
    model = Synthesis
    exclude = ['output', 'output_type', 'prompt']
    readonly_fields = ['synthesis', 'cost']
    verbose_name = ""
    verbose_name_plural = "Syntheses"


class EmbedsInline(ReadOnlyInline):
    model = Embeds
    readonly_fields = ['cost']
    verbose_name = ""
    verbose_name_plural = "Embeds"


class QueryInline(ReadOnlyInline):
    model = Query
    exclude = ['query', 'output', 'prompt']
    readonly_fields = ['synthesis', 'cost']
    verbose_name = ""
    verbose_name_plural = "Queries"


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    """Admin page for the transcript model."""
    form = TranscriptForm
    list_display = ['id', 'title', 'interviewee_names']
    readonly_fields = ['cost', 'metadata_generated']

    def get_inlines(self, request, obj=None):
        return [SynthesisInline, EmbedsInline, QueryInline] \
            if obj else []


@admin.register(Synthesis)
class SynthesisAdmin(admin.ModelAdmin):
    """Admin page for the Synthesis model"""
    list_display = ['transcript', 'output_type', 'synthesis', 'cost']
    fields = ('transcript', 'output_type', 'output',
              'cost', 'synthesis', 'citations', 'prompt')
    readonly_fields = ('cost', 'synthesis', 'citations', 'prompt')


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    """Admin page for the Query model."""
    list_display = ['transcript', 'query', 'synthesis', 'cost']
    fields = ('transcript', 'output', 'cost', 'synthesis',
              'citations', 'prompt')
    readonly_fields = ('cost', 'synthesis', 'citations', 'prompt')
