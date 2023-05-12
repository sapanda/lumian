"""
    Admin pages for the project app.
"""
from django import forms
from django.contrib import admin

from .models import Project
from core.admin import ReadOnlyInline
from transcript.models import Transcript


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'questions': forms.Textarea(attrs={'rows': 10, 'cols': 40}),
        }


class TranscriptInline(ReadOnlyInline):
    model = Transcript
    exclude = ['transcript']
    readonly_fields = ['title', 'interviewee_names',
                       'interviewer_names', 'cost']
    verbose_name = ""
    verbose_name_plural = "Transcripts"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin page for the project model."""
    list_display = ['title', 'user']
    fields = ['title', 'goal', 'questions']
    form = ProjectAdminForm

    def get_inlines(self, request, obj=None):
        return [TranscriptInline] if obj else []
