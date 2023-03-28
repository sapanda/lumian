"""
    Admin pages for the transcript app.
"""
from django import forms
from django.contrib import admin

from transcript.models import (
    Transcript, AIChunks, AISynthesis, AIEmbeds, Query, Synthesis
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


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(AIChunks)
class AIChunksAdmin(ReadOnlyAdmin):
    """Admin page for the AI synthesis model."""
    list_display = ['transcript', 'chunk_type', 'cost']


@admin.register(AISynthesis)
class AISynthesisAdmin(ReadOnlyAdmin):
    """Admin page for the AI synthesis model."""
    list_display = ['transcript', 'output_type', 'total_cost']


@admin.register(AIEmbeds)
class AIEmbedsAdmin(ReadOnlyAdmin):
    """Admin page for the AI synthesis model."""
    list_display = ['transcript', 'index_cost']


@admin.register(Query)
class QueryAdmin(ReadOnlyAdmin):
    """Admin page for the Query model."""
    list_display = ['transcript', 'query', 'query_cost']


class ReadOnlyInline(admin.StackedInline):
    show_change_link = True
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return False


class AIChunksInline(ReadOnlyInline):
    model = AIChunks
    exclude = [field.name for field in AIChunks._meta.get_fields()]
    verbose_name = ""
    verbose_name_plural = "AI Chunks"


class AISynthesisInline(ReadOnlyInline):
    model = AISynthesis
    verbose_name = ""
    verbose_name_plural = "AI Synthesis"
    exclude = ['model_name', 'tokens_used']


class AIEmbedsInline(ReadOnlyInline):
    model = AIEmbeds
    exclude = ['chunks', 'pinecone_ids']
    verbose_name = ""
    verbose_name_plural = "AI Embeds"


class QueryInline(ReadOnlyInline):
    model = Query
    exclude = ['search_values', 'search_scores']
    verbose_name = ""
    verbose_name_plural = "Queries"


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    """Admin page for the transcript model."""
    form = TranscriptForm
    list_display = ['title', 'interviewee_names']

    def get_inlines(self, request, obj=None):
        return [AISynthesisInline, QueryInline,
                AIChunksInline, AIEmbedsInline] \
            if obj else []


@admin.register(Synthesis)
class SynthesisAdmin(admin.ModelAdmin):
    """Admin page for the Synthesis model"""
    list_display = ['transcript', 'output_type', 'summary', 'cost']
    fields = ('transcript', 'output_type', 'output',
              'cost', 'summary', 'reverse_lookups')
    readonly_fields = ('cost', 'summary', 'reverse_lookups')
