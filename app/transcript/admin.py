"""
    Admin pages for the transcript app.
"""
from django import forms
from django.contrib import admin

from transcript import models


class TranscriptForm(forms.ModelForm):
    file = forms.FileField(label='Upload Transcript', required=False)

    class Meta:
        model = models.Transcript
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('file'):
            file_content = self.cleaned_data['file'].read().decode('utf-8')
            instance.transcript = file_content
        if commit:
            instance.save()
        return instance


class TranscriptAdmin(admin.ModelAdmin):
    """Admin page for the transcript model."""
    form = TranscriptForm


class AISynthesisAdmin(admin.ModelAdmin):
    """Admin page for the AI synthesis model."""
    readonly_fields = ['output_type', 'output', 'transcript']


admin.site.register(models.Transcript, TranscriptAdmin)
admin.site.register(models.AISynthesis)
