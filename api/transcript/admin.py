"""
    Admin pages for the transcript app.
"""
from django import forms
from django.contrib import admin
from django.db import transaction
from project.models import Project

from core.admin import ReadOnlyInline
from transcript.models import (
    Transcript, Synthesis, Embeds, Query
)
from transcript.repository import create_synthesis_entry


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
    readonly_fields = ['synthesis', 'cost', 'status']
    verbose_name = ""
    verbose_name_plural = "Syntheses"


class EmbedsInline(ReadOnlyInline):
    model = Embeds
    readonly_fields = ['cost', 'status']
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
    list_display = ['id', 'title', 'interviewee_names', 'start_time']
    readonly_fields = ['cost', 'metadata_generated']

    def save_model(self, request, obj, form, change):
        """Save the transcript model and related objects."""
        if not change:
            # Only perform these actions when creating a new object
            project_id = request.POST.get('project')
            if not project_id:
                raise forms.ValidationError(
                    {"project": "This field is required."}
                )

            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                raise forms.ValidationError({"project": "Invalid project ID."})

            if project.user != request.user:
                raise forms.ValidationError(
                    {"project": "Project doesn't belong to requesting user"}
                )

            with transaction.atomic():
                obj.save()
                create_synthesis_entry(obj)

        else:
            obj.save()

    def get_inlines(self, request, obj=None):
        return [SynthesisInline, EmbedsInline, QueryInline] \
            if obj else []


@admin.register(Synthesis)
class SynthesisAdmin(admin.ModelAdmin):
    """Admin page for the Synthesis model"""
    list_display = ['transcript', 'output_type', 'synthesis', 'cost',
                    'transcript_timestamp']
    fields = ('transcript', 'output_type', 'output',
              'cost', 'synthesis', 'citations', 'prompt', 'status')
    readonly_fields = ('cost', 'synthesis', 'citations', 'prompt', 'status')

    def transcript_timestamp(self, obj):
        return obj.transcript.start_time


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    """Admin page for the Query model."""
    list_display = ['transcript', 'query', 'synthesis', 'cost']
    fields = ('transcript', 'output', 'cost', 'synthesis',
              'citations', 'prompt')
    readonly_fields = ('cost', 'synthesis', 'citations', 'prompt')
